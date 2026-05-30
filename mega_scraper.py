import os
import json
import re
import time
import random
import urllib.request

def save_product_data(category_name, products):
    clean_cat_name = re.sub(r'[^a-zA-Z0-9_]', '_', category_name).lower()
    folder_path = f"data/{clean_cat_name}"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    chunk_size = 500
    for i in range(0, len(products), chunk_size):
        page_num = (i // chunk_size) + 1
        chunk = products[i:i + chunk_size]
        
        file_path = f"{folder_path}/page_{page_num}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=4)
    print(f" Saved {len(products)} products to {folder_path}")

def fetch_category_data(cat_id, cat_name):
    print(f"Fetching Data for Mobile Category: {cat_name} (ID: {cat_id})")
    all_products = []
    
    # စမ်းသပ်မှုအရ အရင်ဆုံး Page ၁ ကို အရင်ဆွဲမည်
    for page in range(1, 4):
        api_url = f"https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/{cat_id}?page={page}&render=json"
        
        # ဖုန်းအစစ်မှ တောင်းဆိုနေသကဲ့သို့ ဟန်ဆောင်ခြင်း
        req = urllib.request.Request(
            api_url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://pages.shop.com.mm/'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    html = response.read().decode('utf-8')
                    json_data = json.loads(html)
                    
                    modules = json_data.get('data', {}).get('modules', [])
                    for module in modules:
                        items = module.get('data', {}).get('list', []) or module.get('data', {}).get('products', [])
                        for item in items:
                            title = item.get('name') or item.get('title')
                            price_str = str(item.get('price', ''))
                            
                            if title and price_str:
                                raw_price = re.sub(r'[^0-9]', '', price_str)
                                if raw_price:
                                    original_price = int(raw_price)
                                    if original_price > 0:
                                        discount_price = int(original_price * 0.45)
                                        
                                        all_products.append({
                                            "title": title.strip(),
                                            "image": item.get('image') or item.get('imgUrl') or "",
                                            "original_price": f"Ks {original_price:,}",
                                            "discount_price": f"Ks {discount_price:,}",
                                            "status": "In Stock"
                                        })
                else:
                    print(f"⚠️ Page {page} returned status: {response.status}")
        except Exception as e:
            print(f" Error fetching page {page}: {e}")
            
        time.sleep(random.uniform(3, 5))
        
    return all_products

def main():
    # သီစုပြထားသော ဘယ်ဘက်ဘေးက Mobile Tabs IDs
    categories = {
        "just_for_you": "just-for-you",
        "health_and_beauty": "health-beauty",
        "tv_and_home_appliances": "tv-home-appliances",
        "groceries_and_pets": "groceries-pets",
        "babies_and_toys": "babies-toys",
        "electronic_devices": "electronic-devices",

"electronic_accessories": "electronic-accessories",
        "womens_fashion": "womens-fashion",
        "home_and_lifestyle": "home-lifestyle",
        "watches_and_accessories": "watches-accessories",
        "mens_fashion": "mens-fashion"
    }
    
    print(f"Starting Base Scraper Engine for {len(categories)} Categories...")
    
    for cat_name, cat_id in categories.items():
        products = fetch_category_data(cat_id, cat_name)
        if products:
            save_product_data(cat_name, products)
        time.sleep(random.uniform(4, 6))

if name == "main":
    main()
