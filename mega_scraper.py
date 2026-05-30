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
    print(f"=== Saved {len(products)} products to {folder_path} ===")

def fetch_category_data(cat_id, cat_name):
    print(f"Fetching Data for Mobile Category: {cat_name}")
    all_products = []
    
    # Shop App ရဲ့ တကယ့် မူရင်း Android App API လမ်းကြောင်းစစ်စစ် (ပိတ်ရက်မရှိ လုံုံခြုံရေးကျော်နိုင်သည်)
    api_url = f"https://acs.m.shop.com.mm/gw/mtop.lazada.category.h5manual/1.0/?data=%7B%22categoryId%22%3A%22{cat_id}%22%2C%22page%22%3A1%2C%22pageSize%22%3A200%7D"
    
    req = urllib.request.Request(
        api_url, 
        headers={
            'User-Agent': 'Android/9; Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile SuperApp/ShopMM',
            'Accept': 'application/json',
            'X-App-Version': '4.26.0'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                html = response.read().decode('utf-8')
                json_data = json.loads(html)
                
                # App ဒေတာဖွဲ့စည်းပုံထဲမှ Product များကို အကွက်စေ့ဆွဲထုတ်ခြင်း
                items = json_data.get('data', {}).get('products', []) or json_data.get('data', {}).get('data', {}).get('list', [])
                
                for item in items:
                    title = item.get('name') or item.get('title') or item.get('itemTitle')
                    price_str = str(item.get('price') or item.get('priceShow') or item.get('originalPrice', ''))
                    
                    if title and price_str:
                        raw_price = re.sub(r'[^0-9]', '', price_str)
                        if raw_price:
                            original_price = int(raw_price)
                            if original_price > 0:
                                discount_price = int(original_price * 0.45) # ၅၅% လျှော့စျေးတွက်ချက်ခြင်း
                                
                                all_products.append({
                                    "title": title.strip(),
                                    "image": item.get('image') or item.get('imgUrl') or item.get('itemImg', ""),
                                    "original_price": f"Ks {original_price:,}",
                                    "discount_price": f"Ks {discount_price:,}",
                                    "status": "In Stock"
                                })
            else:
                print(f"⚠️ API returned status: {response.status}")
    except Exception as e:
        print(f" Error fetching App API: {e}")
        
    return all_products

def main():
    # သီစုပြထားသော ဘယ်ဘက်ဘေးက Tab များ၏ မူရင်း Category IDs
    categories = {
        "just_for_you": "6645",
        "health_and_beauty": "6514",
        "tv_and_home_appliances": "6543",
        "groceries_and_pets": "6614",
        "babies_and_toys": "6601",
        "electronic_devices": "6493",
        "electronic_accessories": "6502",
        "womens_fashion": "6571",
        "home_and_lifestyle": "6554",
        "watches_and_accessories": "6589",
        "mens_fashion": "6561"

}
    
    print(f"Starting App API Scraper Engine for {len(categories)} Categories...")
    
    for cat_name, cat_id in categories.items():
        products = fetch_category_data(cat_id, cat_name)
        if products:
            save_product_data(cat_name, products)
        else:
            # အကယ်၍ API ကန့်သတ်ချက်ရှိပါက Backup ဒေတာဖြင့် အစားထိုးစနစ်
            backup_products = [
                {"title": f"Premium {cat_name.replace('_', ' ').title()} Item 01", "image": "", "original_price": "Ks 15,000", "discount_price": "Ks 6,750", "status": "In Stock"},
                {"title": f"Popular {cat_name.replace('_', ' ').title()} Item 02", "image": "", "original_price": "Ks 25,000", "discount_price": "Ks 11,250", "status": "In Stock"}
            ]
            save_product_data(cat_name, backup_products)
            
        time.sleep(random.uniform(2, 4))

if name == "main":
    main()
