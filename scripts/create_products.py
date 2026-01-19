import csv
import os
import copy
import xml.etree.ElementTree as ET
import requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

API_KEY = "LXUN9PBE66LRHHTU68ZACQARMWYIWVBN"
API_URL = "http://localhost:8080/api/"
CSV_FILE = "data.csv"


# ====== FUNKCJE POMOCNICZE ======
def set_xml_value(xml_root, tag_name, value):
    """Ustawia wartość tagu dla języków 1 i 2 w PrestaShop XML."""
    node = xml_root.find(".//" + tag_name)
    if node is not None:
        for child in list(node):
            node.remove(child)
        lang1 = ET.SubElement(node, "language")
        lang1.set("id", "1")
        lang1.text = value
        lang2 = ET.SubElement(node, "language")
        lang2.set("id", "2")
        lang2.text = value


def clean_product_xml(xml):
    product = xml.find("product")
    if product is None:
        return xml
    keep_tags = ["name", "price", "active", "id_category_default", "link_rewrite", "visibility", "associations",
                 "show_price", "available_for_order", "state", "description"]
    for child in list(product):
        if child.tag not in keep_tags:
            product.remove(child)
    return xml


# ====== KATEGORIE ======
def create_category(name, parent_id):
    template = requests.get(API_URL + "categories?schema=blank", auth=(API_KEY, "")).text
    xml = ET.fromstring(template)
    xml.find(".//id_parent").text = str(parent_id)
    xml.find(".//active").text = "1"

    name_text = name
    link_rewrite_text = name.lower().replace(" ", "-")

    set_xml_value(xml, "name", name_text)
    set_xml_value(xml, "link_rewrite", link_rewrite_text)

    xml_data = ET.tostring(xml, encoding="utf-8")
    r = requests.post(API_URL + "categories", data=xml_data, auth=(API_KEY, ""),
                      headers={"Content-Type": "application/xml"})
    if r.status_code not in [200, 201]:
        print("Błąd podczas tworzenia kategorii:", name, r.text)
        return None

    safe_name = quote(name)
    created = requests.get(API_URL + "categories?filter[name]={}".format(safe_name), auth=(API_KEY, "")).text
    root = ET.fromstring(created)
    category_elem = root.find(".//category")

    if category_elem is not None:
        return category_elem.get("id")
    else:
        post_root = ET.fromstring(r.content)
        return post_root.find(".//id").text


def add_path(path, categories_map):
    parts = [p.strip() for p in path.split("/") if p.strip()]
    parent = categories_map["Strona główna"]
    full = ""
    for part in parts:
        full = part if not full else full + "/" + part
        if full not in categories_map:
            cid = create_category(part, parent)
            if cid is None:
                print("Nie udało się utworzyć kategorii:", full)
                return None
            categories_map[full] = int(cid)
            parent = int(cid)
        else:
            parent = categories_map[full]


# ====== PRODUKTY ======
def create_product(name, price, category_id, description="", active=1):
    template = requests.get(API_URL + "products?schema=blank", auth=(API_KEY, "")).text
    xml = ET.fromstring(template)

    link_rewrite_text = name.lower().replace(" ", "-")

    set_xml_value(xml, "name", name)
    set_xml_value(xml, "description", description)
    set_xml_value(xml, "link_rewrite", link_rewrite_text)

    xml.find(".//price").text = str(price)
    xml.find(".//state").text = "1"
    xml.find(".//show_price").text = "1"
    xml.find(".//available_for_order").text = "1"
    xml.find(".//active").text = str(active)
    xml.find(".//visibility").text = "both"
    xml.find(".//id_category_default").text = str(category_id)

    cats = xml.find(".//associations/categories")
    if cats is not None:
        for child in list(cats):
            cats.remove(child)
        cat_node = ET.SubElement(cats, "category")
        cat_id_node = ET.SubElement(cat_node, "id")
        cat_id_node.text = str(category_id)

    xml = clean_product_xml(xml)
    xml_data = ET.tostring(xml, encoding="utf-8")

    r = requests.post(API_URL + "products", data=xml_data,
                      auth=(API_KEY, ""), headers={"Content-Type": "application/xml"})
    if r.status_code not in [200, 201]:
        print("Błąd podczas tworzenia produktu:", name, r.text)
        return None

    post_root = ET.fromstring(r.content)
    prod_node = post_root.find(".//product")
    if prod_node is not None:
        return prod_node.find("id").text

    return None


def set_product_stock(product_id, quantity):
    r = requests.get(f"{API_URL}stock_availables?filter[id_product]={product_id}&display=full", auth=(API_KEY, ""))
    if r.status_code != 200:
        print(f"Nie udało się pobrać stocku dla produktu ID {product_id}: {r.status_code}\n{r.text}")
        return

    root = ET.fromstring(r.content)
    stock = root.find(".//stock_available")
    if stock is None:
        print(f"Brak wpisu stock_available dla produktu ID {product_id}")
        return

    sid_node = stock.find("id")
    if sid_node is None or not sid_node.text:
        print(f"Brak ID stock_available dla produktu ID {product_id}")
        return

    root_payload = ET.Element("prestashop")
    stock_payload = copy.deepcopy(stock)
    root_payload.append(stock_payload)

    stock_payload.find("quantity").text = str(quantity)
    stock_payload.find("depends_on_stock").text = "0"
    stock_payload.find("out_of_stock").text = "2"
    xml_data = ET.tostring(root_payload, encoding="utf-8")
    r = requests.put(f"{API_URL}stock_availables/{sid_node.text}", data=xml_data,
                     auth=(API_KEY, ""), headers={"Content-Type": "application/xml"})
    if r.status_code in [200, 201]:
        print(f"Zaktualizowano stock produktu ID {product_id} do {quantity}")
    else:
        print(f"Błąd aktualizacji stocku produktu ID {product_id}: {r.status_code}\n{r.text}")


def add_image_to_product(product_id, image_url):
    try:
        r = requests.get(image_url)
        if r.status_code != 200:
            print("Nie udało się pobrać obrazka:", image_url)
            return
        img = Image.open(BytesIO(r.content))
        img = img.convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=90)
        buf.seek(0)
        files = {"image": (os.path.basename(image_url), buf, "image/jpeg")}
        upload = requests.post(
            API_URL + f"images/products/{product_id}",
            auth=(API_KEY, ""),
            files=files
        )
        if upload.status_code in [200, 201]:
            print("Dodano obrazek do produktu ID", product_id)
        else:
            print("Błąd dodawania obrazka:", upload.text)
    except Exception as e:
        print("Wyjątek przy dodawaniu obrazka:", e)


def ensure_attribute_group(name):
    """Tworzy grupę atrybutów np. Smak jeśli nie istnieje."""
    safe_name = quote(name)
    # Sprawdzamy czy istnieje
    res = requests.get(API_URL + f"product_options?filter[name]={safe_name}", auth=(API_KEY, "")).text
    root = ET.fromstring(res)
    node = root.find(".//product_option")
    
    if node is not None:
        # --- POPRAWKA ---
        # W widoku listy ID jest atrybutem tagu, a nie pod-elementem.
        return node.get("id")
        # ----------------

    # Jeśli nie istnieje, tworzymy
    template = requests.get(API_URL + "product_options?schema=blank", auth=(API_KEY, "")).text
    xml = ET.fromstring(template)
    
    set_xml_value(xml, "name", name)
    set_xml_value(xml, "public_name", name)
    
    group_type = xml.find(".//group_type")
    if group_type is not None:
        group_type.text = "select"
    
    xml_data = ET.tostring(xml, encoding="utf-8")
    r = requests.post(API_URL + "product_options", data=xml_data, auth=(API_KEY, ""),
                      headers={"Content-Type": "application/xml"})
    
    if r.status_code in [200, 201]:
        post_root = ET.fromstring(r.content)
        return post_root.find(".//id").text
    else:
        print(f"Błąd tworzenia grupy atrybutów '{name}': {r.text}")
        return None

def ensure_attribute_value(group_id, value_name):
    """Tworzy wartość atrybutu w grupie Smak i zwraca ID."""
    safe_name = quote(value_name)
    # Filtrujemy po nazwie ORAZ po ID grupy, żeby uniknąć konfliktów
    res = requests.get(API_URL + f"product_option_values?filter[name]={safe_name}&filter[id_attribute_group]={group_id}", auth=(API_KEY, "")).text
    root = ET.fromstring(res)
    node = root.find(".//product_option_value")
    
    if node is not None:
        # --- POPRAWKA ---
        return node.get("id")
        # ----------------

    template = requests.get(API_URL + "product_option_values?schema=blank", auth=(API_KEY, "")).text
    xml = ET.fromstring(template)
    set_xml_value(xml, "name", value_name)
    xml.find(".//id_attribute_group").text = str(group_id)
    
    xml_data = ET.tostring(xml, encoding="utf-8")
    r = requests.post(API_URL + "product_option_values", data=xml_data, auth=(API_KEY, ""),
                      headers={"Content-Type": "application/xml"})
    if r.status_code in [200, 201]:
        post_root = ET.fromstring(r.content)
        return post_root.find(".//id").text
    return None

def set_combination_stock(product_id, attribute_id, quantity):
    """Ustawia stock dla konkretnego wariantu (kombinacji)."""
    # Szukamy wpisu stock_available dla danego produktu I wariantu
    url = f"{API_URL}stock_availables?filter[id_product]={product_id}&filter[id_product_attribute]={attribute_id}&display=full"
    r = requests.get(url, auth=(API_KEY, ""))
    
    if r.status_code != 200:
        print(f"Błąd pobierania stocku dla wariantu {attribute_id}: {r.text}")
        return

    root = ET.fromstring(r.content)
    stock = root.find(".//stock_available")
    
    if stock is None:
        print(f"Nie znaleziono wpisu stock_available dla produktu {product_id} i wariantu {attribute_id}")
        return

    stock_id = stock.find("id").text

    # Budujemy XML do aktualizacji
    root_payload = ET.Element("prestashop")
    stock_payload = copy.deepcopy(stock)
    root_payload.append(stock_payload)

    stock_payload.find("quantity").text = str(quantity)
    stock_payload.find("depends_on_stock").text = "0" 
    stock_payload.find("out_of_stock").text = "2" # 2 = użyj domyślnych ustawień (np. pozwalaj zamawiać lub nie)

    xml_data = ET.tostring(root_payload, encoding="utf-8")
    
    # Wysyłamy PUT
    r = requests.put(f"{API_URL}stock_availables/{stock_id}", data=xml_data,
                     auth=(API_KEY, ""), headers={"Content-Type": "application/xml"})
    
    if r.status_code not in [200, 201]:
        print(f"Błąd aktualizacji stocku wariantu {attribute_id}: {r.text}")
    # else:
    #     print(f"Zaktualizowano stock wariantu {attribute_id} do {quantity}")


def add_product_tastes(product_id, tastes_str):
    """Dodaje smaki produktu jako kombinacje (variations)."""
    if not tastes_str.strip():
        return

    tastes = [t.strip() for t in tastes_str.split("|") if t.strip()]
    if not tastes:
        return

    # Używamy poprawionej wcześniej funkcji ensure_attribute_group
    group_id = ensure_attribute_group("Smak")
    if not group_id:
        print("Nie udało się utworzyć grupy Smak")
        return

    first_combination = True

    for taste in tastes:
        # Używamy poprawionej wcześniej funkcji ensure_attribute_value
        value_id = ensure_attribute_value(group_id, taste)
        if not value_id:
            print(f"Nie udało się utworzyć wartości Smak: {taste}")
            continue

        template = requests.get(API_URL + "combinations?schema=blank", auth=(API_KEY, "")).text
        xml = ET.fromstring(template)
        
        xml.find(".//id_product").text = str(product_id)
        xml.find(".//minimal_quantity").text = "1"
        xml.find(".//quantity").text = "0" # Tu wpisujemy 0, bo stock i tak nadpiszemy funkcją
        xml.find(".//price").text = "0.00"
        xml.find(".//unit_price_impact").text = "0.00"
        
        default_on_node = xml.find(".//default_on")
        if default_on_node is not None:
            default_on_node.text = "1" if first_combination else "0"
        else:
            do = ET.SubElement(xml, "default_on")
            do.text = "1" if first_combination else "0"
            
        first_combination = False

        associations = xml.find(".//associations/product_option_values")
        if associations is not None:
             val_node = ET.SubElement(associations, "product_option_value")
             id_node = ET.SubElement(val_node, "id")
             id_node.text = str(value_id)
        
        xml_data = ET.tostring(xml, encoding="utf-8")
        r = requests.post(API_URL + "combinations", data=xml_data, auth=(API_KEY, ""),
                          headers={"Content-Type": "application/xml"})
        
        if r.status_code in [200, 201]:
            # --- KLUCZOWA ZMIANA ---
            # Pobieramy ID nowo utworzonej kombinacji z odpowiedzi
            resp_root = ET.fromstring(r.content)
            combination_id = resp_root.find(".//id").text
            
            print(f"Dodano kombinację smak: {taste} (ID: {combination_id}) -> Aktualizacja stocku...")
            
            # Ustawiamy stock dla tej konkretnej kombinacji na 10 sztuk
            set_combination_stock(product_id, combination_id, 10)
            # -----------------------
        else:
            print(f"Błąd dodawania kombinacji: {taste} do produktu ID {product_id}\n{r.text}")


categories_map = {"Strona główna": 2}

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        path = row["category"]
        add_path(path, categories_map)

for k, v in categories_map.items():
    print(v, "→", k)

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        category_path = row["category"]
        category_id = categories_map.get(category_path)
        print("ID:", category_id)
        if category_id:
            pid = create_product(
                name=row["name"],
                price=row["price"],
                category_id=category_id,
                description=row.get("description_text", ""),
                active=1
            )
            if pid:
                print("Produkt utworzony:", row["name"], "ID:", pid)
                add_image_to_product(pid, row["main_image"])
                set_product_stock(pid, 10)
                add_product_tastes(pid, row.get("tastes", ""))