import requests
from bs4 import BeautifulSoup
import json
import os

# Data များကို စနစ်တကျ Category အလိုက် Folder ဖွဲ့ပြီး သိမ်းမည့် Function
def save_product_data(category, products):
    folder_path = f"data/{category}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path) # Folder မရှိသေးလျှင် အလိုအလျောက် ဆောက်သည်
        
    # ပစ္စည်း ၁,၀၀၀ စီကို ဖိုင်တစ်ဖိုင်စီ ခွဲသိမ်းခြင်း (Pagination)
    chunk_size = 1000
    for i in range(0, len(products), chunk_size):
        page_num = (i // chunk_size) + 1
        chunk = products[i:i + chunk_size]
        
        file_path = f"{folder_path}/page_{page_num}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(chunk)} products to {file_path}")

def start_scraping():
    # နမူနာဆွဲမည့် Category စာရင်း (နောက်ပိုင်း မိမိစိတ်ကြိုက် Link များ ထပ်တိုးနိုင်သည်)
    target_categories = {
        "electronic_devices": "https://www.shop.com.mm/electronic-devices/",
        "men_fashion": "https://www.shop.com.mm/mens-fashion/",
        "women_fashion": "https://www.shop.com.mm/womens-fashion/"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for cat_name, url in target_categories.items():
        print(f"Scraping category: {cat_name}...")
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        scraped_items = []
        
        items = soup.find_all('div', class_='card-jfy-item') or soup.find_all('div', class_='hp-mod-card-item')
        
        for item in items:
            try:
                title = item.find('div', class_='card-jfy-title').text.strip()
                image_url = item.find('img')['src']
                price_text = item.find('span', class_='hp-mod-price').text
                original_price = int(''.join(filter(str.isdigit, price_text)))
                
                # စျေးနှုန်းအား ၅ nose% (၅၅ ရာခိုင်နှုန်း) အလိုအလျောက် လျှော့ချခြင်း
                discounted_price = int(original_price * 0.45) 
                
                scraped_items.append({
                    "title": title,
                    "image": image_url,
                    "original_price": f"Ks {original_price:,}",
                    "discount_price": f"Ks {discounted_price:,}"
                })
            except:
                continue
        
        # ရလာသမျှ ပစ္စည်းရာဂဏန်း/ထောင်ဂဏန်းများကို သက်ဆိုင်ရာ Folder ထဲ ခွဲသိမ်းရန် ပို့လိုက်ခြင်း
        if scraped_items:
            save_product_data(cat_name, scraped_items)

if name == "main":
    start_scraping()
