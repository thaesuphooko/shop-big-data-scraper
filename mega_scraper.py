import asyncio
from playwright.async_api import async_playwright
import json
import os
import re
import random

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
    print(f" Successfully Saved {len(products)} products to {folder_path}")

async def scrape_site_category(context, cat_name, url):
    print(f"Starting Scraper for: {cat_name} -> {url}")
    page = await context.new_page()
    
    # စက်ရုပ်မှန်း သိစေမည့် Webdriver Parameter ကို ဖျောက်ဖျက်ခြင်း (Stealth Mode)
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Website ဆီသို့ သွားခြင်း
        response = await page.goto(url, wait_until="commit", timeout=90000)
        await asyncio.sleep(random.uniform(3, 5)) # လူလိုမျိုး ခဏစောင့်ခြင်း
        
        # စာမျက်နှာအောက်သို့ ဖြည်းဖြည်းချင်း ၆ ကြိမ် Scroll ဆွဲချခြင်း
        for i in range(6):
            await page.evaluate(f"window.scrollBy(0, {random.randint(800, 1200)})")
            await asyncio.sleep(random.uniform(1.5, 2.5))

        # HTML ထဲမှ Data များကို လှမ်းယူခြင်း
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
                        
                        const originalPrice = parseInt(priceText.replace(/[^0-9]/g, ''));
                        if (originalPrice > 0) {
                            const discountPrice = Math.floor(originalPrice * 0.45);
                            
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
        print(f"Skipping {cat_name} due to security/timeout: {e}")
        await page.close()
        return []

async def main():
    async with async_playwright() as p:
        # အပိတ်မခံရစေရန်အတွက် Arguments များ ထပ်မံဖြည့်စွက်ခြင်း
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",

"--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--ignore-certificate-errors"
            ]
        )
        
        # Screen Size နှင့် လူသုံးအများဆုံး User Agent ကို သတ်မှတ်ခြင်း
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        # ဆေးဝါး၊ အိမ်သုံး၊ မိဖိုချောင်သုံး နှင့် ကဏ္ဍစုံ ပင်မ Links များ
        categories = {
            "health_medicine_beauty": "https://www.shop.com.mm/health-beauty/",
            "home_kitchen_lifestyle": "https://www.shop.com.mm/home-lifestyle/",
            "electronic_devices": "https://www.shop.com.mm/electronic-devices/",
            "groceries_supermarket": "https://www.shop.com.mm/groceries-shop/",
            "men_fashion": "https://www.shop.com.mm/mens-fashion/",
            "women_fashion": "https://www.shop.com.mm/womens-fashion/"
        }

        print(f"Initializing Mega Scraper Bot for {len(categories)} Categories...")

        for cat_name, url in categories.items():
            products = await scrape_site_category(context, cat_name, url)
            if products:
                save_product_data(cat_name, products)
            # ဝက်ဘ်ဆိုက်မှ Block မလုပ်နိုင်စေရန် တစ်ခုနှင့်တစ်ခုကြား ၅ စက္ကန့် နားပေးခြင်း
            await asyncio.sleep(5)
                
        await browser.close()

if name == "main":
    asyncio.run(main())
