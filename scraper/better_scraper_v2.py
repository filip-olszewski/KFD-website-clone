from pprint import pprint
import cloudscraper 
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urlparse, urljoin

BASE_URL = "https://sklep.kfd.pl"
OUTPUT_FILE = "kfd_dataset.csv"

how_many_pages_to_parse = 7

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

def scrape_kfd_products():
    base_url = "https://sklep.kfd.pl/sklep-kfd-c-2.html?order=product.sales.desc"
    
    product_links = []
    
    for page in range(1, how_many_pages_to_parse + 1):
        url = f"{base_url}&page={page}"
        
        try:
            delay = random.uniform(3.0, 6.0) 
            time.sleep(delay)
            
            print(f"Scraping Listing Page: {page}...")
            response = scraper.get(url) 
            
            if response.status_code != 200:
                print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.select('.product-title a')
            
            if not links:
                links = soup.select('a.product-name')
            
            if not links:
                links = soup.select('.product-container .product-name a')
            
            if not links:
                print(f"No products found on page {page}, stopping.")
                break
            
            for link in links:
                href = link.get('href')
                if href and href not in product_links:
                    product_links.append(href)
            
            print(f"Page {page}: found {len(links)} products, total: {len(product_links)}")
            
        except Exception as e:
            print(f"An error occurred on page {page}: {e}")
            break

    return product_links

def get_soup(url, referer=None):
    try:
        delay = random.uniform(2.5, 5.0) 
        time.sleep(delay)
        
        # Update headers specifically for this request to include Referer
        headers = {}
        if referer:
            headers['Referer'] = referer

        response = scraper.get(url, headers=headers, timeout=20)
        
        if response.status_code == 403:
            print(f"[BLOCKED] 403 Forbidden on {url}. Waiting 30s...")
            time.sleep(30)
            return None
            
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None

def clean_text(text):
    if text:
        return " ".join(text.split())
    return ""

def extract_plain_text(element):
    if not element:
        return ""
    text = element.get_text(separator="\n")
    lines = [clean_text(line) for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    return "\n".join(non_empty)

def extract_gallery_images(soup):
    gallery_images = []
    if not isinstance(soup, BeautifulSoup):
        return gallery_images

    seen = set()
    for img in soup.select("ul.product-images img"):
        img_url = img.get("data-image-medium-src")

        if not img_url:
            continue

        full_url = img_url if img_url.startswith("http") else urljoin(BASE_URL, img_url)
        if full_url not in seen:
            seen.add(full_url)
            gallery_images.append(full_url)

    return gallery_images

def extract_similar_products(soup):
    similar_links = []
    similar_images = []
    if not isinstance(soup, BeautifulSoup):
        return similar_links, similar_images

    seen = set()
    for product_tile in soup.select("div.products div.productmorelikethat article"):
        anchor = product_tile.select_one(".product-description a") or product_tile.select_one("a")
        if not anchor:
            continue

        href = anchor.get("href")
        if not href:
            continue

        full_url = href if href.startswith("http") else urljoin(BASE_URL, href)
        if full_url in seen:
            continue

        seen.add(full_url)
        similar_links.append(full_url)

        img_tag = product_tile.select_one("img")
        img_src = (img_tag.get("data-full-size-image-url")
                   or img_tag.get("data-src")
                   or img_tag.get("src")) if img_tag else None
        if img_src:
            img_url = img_src if img_src.startswith("http") else urljoin(BASE_URL, img_src)
        else:
            img_url = ""
        similar_images.append(img_url)

    return similar_links, similar_images

def parse_product_details(product_url):
    # Pass the listing page as the 'Referer' to look natural
    referer = "https://sklep.kfd.pl/sklep-kfd-c-2.html"
    soup = get_soup(product_url, referer=referer)
   
    if not soup:
        return None

    item = {
        "active": 1,
        "name": "",
        "category": "", 
        "description_text": "",
        "description_html": "",
        "price": "",
        "main_image": "",
        "gallery_images": [],
        "tastes": [],
        "similar_products": [],
        "similar_product_images": []
    }

    h1 = soup.find("h1")
    item["name"] = clean_text(h1.get_text()) if h1 else "Unknown"

    breadcrumb_nav = soup.find("nav", class_="breadcrumb") or soup.find("div", class_="breadcrumb")
    breadcrumb_segments = []
    if breadcrumb_nav:
        links = breadcrumb_nav.find_all("a")
        breadcrumb_segments = [clean_text(a.get_text()) for a in links]

        last_span = breadcrumb_nav.find("span", class_="navigation-pipe")
        if last_span and last_span.next_sibling:
            current_page_text = str(last_span.next_sibling).strip()
            if current_page_text:
                breadcrumb_segments.append(clean_text(current_page_text))

    filtered_segments = [segment for segment in breadcrumb_segments if segment and segment.lower()]
    if filtered_segments:
        item["category"] = "/".join(filtered_segments)

    price_span = soup.find("span", class_="current-price-value")
    if price_span:
        price_text = price_span.get("content") or price_span.get_text()
        item["price"] = clean_text(price_text).replace("\xa0zł", "").strip()
    else:
        item["price"] = "0"

    cover_img = soup.find("img", class_="js-qv-product-cover")
    if cover_img and cover_img.get("src"):
        cover_src = cover_img["src"]
        item["main_image"] = cover_src if cover_src.startswith("http") else urljoin(BASE_URL, cover_src)

    gallery_images = extract_gallery_images(soup)
    if gallery_images:
        item["gallery_images"] = gallery_images
        if not item["main_image"]:
            item["main_image"] = gallery_images[0]

    tastes = []
    tastes_select = soup.find("select", id="group_4") or soup.find(
        "select", attrs={"data-product-attribute": "4"}
    ) or soup.find("select", attrs={"name": "group[4]"})

    if tastes_select:
        for option in tastes_select.find_all("option"):
            flavor = clean_text(option.get("title") or option.get_text())
            if flavor:
                tastes.append(flavor)

    item["tastes"] = tastes

    similar_links, similar_images = extract_similar_products(soup)
    item["similar_products"] = similar_links
    item["similar_product_images"] = similar_images

    description_tab = soup.find("div", id="description")
    if description_tab:
        description_div = description_tab.find("div", class_="product-description")
        if description_div:
            item["description_text"] = extract_plain_text(description_div)
            item["description_html"] = str(description_div)
    
    return item

def main():
    print("Starting scrape...")
    links_to_parse = scrape_kfd_products()
    pprint(f"Total product links to parse: {len(links_to_parse)}")

    all_products = []
    
    for i, link in enumerate(links_to_parse):
        print(f"[{i+1}/{len(links_to_parse)}] Processing: {link}")
        x = parse_product_details(link)
        if x:
            all_products.append(x)
        
        # Save explicitly every 5 items to avoid losing data on crash
        if i % 5 == 0 and all_products:
             save_to_csv(all_products)

    save_to_csv(all_products)

def save_to_csv(all_products):
    if not all_products:
        return

    with open("kfd_dataset.csv", "w", encoding="utf-8", newline='') as fx:
        fieldnames = [
            "name","active",  "category", "description_text", "description_html",
            "price", "main_image", "gallery_images",
            "tastes", "similar_products", "similar_product_images"
        ]
        writer = csv.DictWriter(fx, fieldnames=fieldnames)
        writer.writeheader()
        
        for product in all_products:
            row = product.copy()
            row["gallery_images"] = "|".join(row["gallery_images"]) if row["gallery_images"] else ""
            row["tastes"] = "|".join(row["tastes"]) if row["tastes"] else ""
            row["similar_products"] = "|".join(row["similar_products"]) if row["similar_products"] else ""
            row["similar_product_images"] = "|".join(row["similar_product_images"]) if row["similar_product_images"] else ""
            writer.writerow(row)
    print("Saved progress to kfd_dataset.csv")

if __name__ == "__main__":
    main()