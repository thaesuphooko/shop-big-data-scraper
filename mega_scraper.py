import os
import json
import re
import time
import random
import cloudscraper

def save_product_data(category_name, products):
    clean_cat_name = re.sub(r'[^a-zA-Z0-9_]', '_', category_name).lower()
    folder_path = f"data/{clean_cat_name}"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    # ပစ္စည်း ၅၀၀ စီ ခွဲပြီး File များခွဲသိမ်းခြင်း
    chunk_size = 500
    for i in range(0, len(products), chunk_size):
        page_num = (i // chunk_size) + 1
        chunk = products[i:i + chunk_size]
        
        file_path = f"{folder_path}/page_{page_num}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=4)
    print(f" Saved {len(products)} products to {folder_path}")

def fetch_category_data(scraper, cat_id, cat_name):
    print(f"Fetching Data for Mobile Category: {cat_name} (ID: {cat_id})")
    all_products = []
    
    # ပစ္စည်းအစုံအလင်ရရန် Page ၅ ခုအထိ ပတ်ဆွဲခြင်း
    for page in range(1, 6):
        # Shop Mobile App API ရဲ့ တကယ့် နောက်ကွယ်က Data ပေးပို့သည့် လမ်းကြောင်းအမှန်
        api_url = f"https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/{cat_id}?page={page}&render=json"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://pages.shop.com.mm/"
        }
        
        try:
            response = scraper.get(api_url, headers=headers, timeout=30)
            if response.status_code == 200:
                json_data = response.json()
                
                # Shop API ရဲ့ JSON တည်ဆောက်ပုံထဲမှ ပစ္စည်းများကို ရှာဖွေဖော်ထုတ်ခြင်း
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
                                    discount_price = int(original_price * 0.45) # ၅၅% လျှော့စျေးတွက်ခြင်း
                                    
                                    all_products.append({
                                        "title": title.strip(),
                                        "image": item.get('image') or item.get('imgUrl') or "",
                                        "original_price": f"Ks {original_price:,}",
                                        "discount_price": f"Ks {discount_price:,}",
                                        "status": "In Stock"
                                    })
            else:
                print(f"⚠️ Page {page} returned status code: {response.status_code}")
        except Exception as e:
            print(f" Error fetching page {page}: {e}")
            
        time.sleep(random.uniform(2, 4)) # Block မဖြစ်အောင် ခဏနားပေးခြင်း
        
    return all_products

def main():
    # Cloudflare လုံခြုံရေးကို အလိုအလျောက် ကျော်ဖြတ်ပေးမည့် Scraper အား အသက်သွင်းခြင်း
    scraper = cloudscraper.create_scraper()
    
    # သီစုပြထားသော ဘယ်ဘက်ဘေးက Mobile Tabs စစ်စစ်များ၏ API IDs
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
    
    print(f"Starting Mega Smart Scraper Engine for {len(categories)} Mobile Categories...")
    
    for cat_name, cat_id in categories.items():
        products = fetch_category_data(scraper, cat_id, cat_name)
        if products:
            save_product_data(cat_name, products)
        time.sleep(random.uniform(3, 5))

if name == "main":
    main()
