import asyncio
from playwright.async_api import async_playwright
import json
import os
import re

def save_product_data(category_name, products):
    clean_cat_name = re.sub(r'[^a-zA-Z0-9_]', '_', category_name).lower()
    folder_path = f"data/{clean_cat_name}"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    chunk_size = 1000
    for i in range(0, len(products), chunk_size):
        page_num = (i // chunk_size) + 1
        chunk = products[i:i + chunk_size]
        
        file_path = f"{folder_path}/page_{page_num}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=4)
    print(f" Saved {len(products)} products to {folder_path}")

async def scrape_site_category(context, cat_name, url):
    print(f"Scraping Content from: {cat_name} -> {url}")
    page = await context.new_page()
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # ပစ္စည်းများ အားလုံးပွင့်လာအောင် အောက်သို့ Scroll ဆွဲချခြင်း
        for _ in range(8):
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(2)

        products_data = await page.evaluate('''() => {
            const items = document.querySelectorAll('.card-jfy-item')  document.querySelectorAll('.hp-mod-card-item')  document.querySelectorAll('.item-card');
            const data = [];
            items.forEach(item => {
                try {
                    const titleElement = item.querySelector('.card-jfy-title')  item.querySelector('.hp-mod-card-item-title')  item.querySelector('.title');
                    const priceElement = item.querySelector('.hp-mod-price') || item.querySelector('.price');
                    const imgElement = item.querySelector('img');
                    
                    if (titleElement && priceElement) {
                        const title = titleElement.innerText.trim();
                        const image = imgElement ? imgElement.src : "";
                        const priceText = priceElement.innerText;
                        
                        const originalPrice = parseInt(priceText.replace(/[^0-0]/g, ''));
                        if (originalPrice > 0) {
                            const discountPrice = Math.floor(originalPrice * 0.45); // ၅၅% လျှော့စျေးတွက်ခြင်း
                            
                            data.push({
                                title: title,
                                image: image,
                                original_price: "Ks " + originalPrice.toLocaleString(),
                                discount_price: "Ks " + discountPrice.toLocaleString(),
                                status: "In Stock"
                            });
                        }
                    }
                } catch (e) {}
            });
            return data;
        }''')
        
        await page.close()
        return products_data
    except Exception as e:
        print(f"Error skipping {cat_name}: {e}")
        await page.close()
        return []

async def main():
    async with async_playwright() as p:
        # GitHub Core Environment တွင် အဆင်ပြေပြေ အလုပ်လုပ်နိုင်မည့် Argument များ
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # လူအစစ်နှင့် တူစေရန် User Agent ကို စနစ်တကျ သတ်မှတ်ခြင်း
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

)
        
        # ပင်မစာရင်းများကို ကြိုတင်သတ်မှတ်ပေးထားခြင်း (ဆေးဝါး၊ အိမ်သုံး၊ မိဖိုချောင်သုံး၊ ဖက်ရှင်၊ အကုန်ပါဝင်သည်)
        categories = {
            "health_medicine_beauty": "https://www.shop.com.mm/health-beauty/",
            "home_kitchen_lifestyle": "https://www.shop.com.mm/home-lifestyle/",
            "electronic_devices": "https://www.shop.com.mm/electronic-devices/",
            "groceries_supermarket": "https://www.shop.com.mm/groceries-shop/",
            "men_fashion": "https://www.shop.com.mm/mens-fashion/",
            "women_fashion": "https://www.shop.com.mm/womens-fashion/"
        }

        print(f"Starting Mega Process for {len(categories)} Categories...")

        for cat_name, url in categories.items():
            products = await scrape_site_category(context, cat_name, url)
            if products:
                save_product_data(cat_name, products)
                
        await browser.close()

if name == "main":
    asyncio.run(main())
