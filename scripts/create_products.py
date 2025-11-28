import csv
import os
import copy
import xml.etree.ElementTree as ET
import requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote



API_KEY = "26X8RJPLNRLG3PVLV82KJ866LZV3B6LX"
API_URL = "http://localhost:8080/api/"
CSV_FILE = "kfd_dataset-2.csv"


def clean_product_xml(xml):
    product = xml.find("product")
    if product is None:
        return xml  # nic do czyszczenia
    keep_tags = ["name", "price", "active", "id_category_default", "link_rewrite", "visibility", "associations",
                  "show_price", "available_for_oder", "state", "description"]
    for child in list(product):
        if child.tag not in keep_tags:
            product.remove(child)
    return xml


def create_category(name, parent_id):
    template = requests.get(API_URL + "categories?schema=blank", auth=(API_KEY, "")).text
    xml = ET.fromstring(template)
    xml.find(".//name/language").text = name
    xml.find(".//id_parent").text = str(parent_id)
    xml.find(".//active").text = "1"
    name_text = name
    link_rewrite_text = name.lower().replace(" ", "-")

    xml.find(".//name/language[@id='1']").text = name_text
    xml.find(".//name/language[@id='2']").text = name_text

    xml.find(".//link_rewrite/language[@id='1']").text = link_rewrite_text
    xml.find(".//link_rewrite/language[@id='2']").text = link_rewrite_text
    xml_data = ET.tostring(xml, encoding="utf-8")
    #print("XML do wysłania:\n", ET.tostring(xml, encoding="unicode"))
    r = requests.post(API_URL + "categories", data=xml_data, auth=(API_KEY, ""),
                      headers={"Content-Type": "application/xml"})
    if r.status_code not in [200, 201]:
        print("Błąd podczas tworzenia:", name, r.text)
        return None

    safe_name = quote(name)
    created = requests.get(API_URL + "categories?filter[name]={}".format(safe_name), auth=(API_KEY, "")).text
    #print(created)
    root = ET.fromstring(created)
    #print(root)
    category_elem = root.find(".//category")
    return category_elem.get("id")


def add_path(path, categories_map):
    parts = [p.strip() for p in path.split("/") if p.strip()]
    parent = categories_map["Strona główna"]  # ID root
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


def create_product(name, price, category_id, description="", active=1):
    template = requests.get(API_URL + "products?schema=blank", auth=(API_KEY, "")).text
    xml = ET.fromstring(template)
    #print(template)
    link_rewrite_text = name.lower().replace(" ", "-")
    xml.find(".//name/language[@id='1']").text = name
    xml.find(".//name/language[@id='2']").text = name
    xml.find(".//price").text = str(price)
    xml.find(".//state").text = "1"
    xml.find(".//show_price").text = "1"
    xml.find(".//available_for_order").text = "1"
    xml.find(".//active").text = str(active)
    xml.find(".//visibility").text = "both"
    xml.find(".//id_category_default").text = str(category_id)
    xml.find(".//description/language[@id='1']").text = description
    xml.find(".//description/language[@id='2']").text = description
    xml.find(".//link_rewrite/language[@id='1']").text = link_rewrite_text
    xml.find(".//link_rewrite/language[@id='2']").text = link_rewrite_text
    xml.find(".//associations/categories/category/id").text = str(category_id)
    xml = clean_product_xml(xml)
    xml_data = ET.tostring(xml, encoding="utf-8")
    #print("XML do wysłania:\n", ET.tostring(xml, encoding="unicode"))
    r = requests.post(API_URL + "products", data=xml_data,
                      auth=(API_KEY, ""), headers={"Content-Type": "application/xml"})
    if r.status_code not in [200, 201]:
        print("Błąd podczas tworzenia produktu:", name, r.text)
        return None

    safe_name = quote(name)
    created = requests.get(API_URL + f"products?filter[name]={safe_name}", auth=(API_KEY, "")).text
    #print(created)
    root = ET.fromstring(created)
    product_elem = root.find(".//product")
    if product_elem is not None:
        return product_elem.get("id")
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
        print( "ID:", category_id)
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


