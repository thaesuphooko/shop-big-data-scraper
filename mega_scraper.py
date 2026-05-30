import asyncio
from playwright.async_api import async_playwright
import json
import os
import re
import random

def save_product_data(category_name, products):
    # ကဏ္ဍအမည်ကို Folder Name အဖြစ် ပြောင်းလဲခြင်း
    clean_cat_name = re.sub(r'[^a-zA-Z0-9_]', '_', category_name).lower()
    folder_path = f"data/{clean_cat_name}"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    # ပစ္စည်း ၁၀၀၀ စီ ခွဲပြီး File များခွဲသိမ်းခြင်း
    chunk_size = 1000
    for i in range(0, len(products), chunk_size):
        page_num = (i // chunk_size) + 1
        chunk = products[i:i + chunk_size]
        
        file_path = f"{folder_path}/page_{page_num}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=4)
    print(f" Saved {len(products)} products to folder: {folder_path}")

async def scrape_site_category(context, cat_name, url):
    print(f"Accessing Category: {cat_name} -> {url}")
    page = await context.new_page()
    
    # စက်ရုပ်မှန်းသိစေမည့် Automation Tags များကို လူအစစ်ကဲ့သို့ ဖျောက်ဖျက်ခြင်း
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # ဝက်ဘ်ဆိုက် စာမျက်နှာကို စတင်ခေါ်ယူခြင်း
        await page.goto(url, wait_until="domcontentloaded", timeout=90000)
        await asyncio.sleep(random.uniform(4, 6)) # လူတစ်ယောက်လို ခဏစောင့်ကြည့်ခြင်း
        
        # ကုန်ပစ္စည်းများ အစုံအလင် ထွက်လာစေရန် အောက်သို့ ဖြည်းဖြည်းချင်း ၈ ကြိမ် Scroll ဆွဲချခြင်း
        for i in range(8):
            await page.evaluate(f"window.scrollBy(0, {random.randint(900, 1300)})")
            await asyncio.sleep(random.uniform(2, 3))

        # HTML Structure ထဲမှ ပစ္စည်းအချက်အလက်များကို အလိုအလျောက် ဆွဲထုတ်ခြင်း
        products_data = await page.evaluate('''() => {
            const items = document.querySelectorAll('.card-jfy-item')  document.querySelectorAll('.hp-mod-card-item')  document.querySelectorAll('.item-card') || document.querySelectorAll('[data-qa-locator="product-item"]');
            const data = [];
            items.forEach(item => {
                try {
                    const titleElement = item.querySelector('.card-jfy-title')  item.querySelector('.hp-mod-card-item-title')  item.querySelector('.title') || item.querySelector('.title--w_fXg');
                    const priceElement = item.querySelector('.hp-mod-price')  item.querySelector('.price')  item.querySelector('.price--R500g');
                    const imgElement = item.querySelector('img');
                    
                    if (titleElement && priceElement) {
                        const title = titleElement.innerText.trim();
                        const image = imgElement ? imgElement.src : "";
                        const priceText = priceElement.innerText;
                        
                        // ဂဏန်းသီးသန့် စစ်ထုတ်ယူခြင်း
                        const originalPrice = parseInt(priceText.replace(/[^0-9]/g, ''));
                        if (originalPrice > 0) {
                            const discountPrice = Math.floor(originalPrice * 0.45); // ၅၅% လျှော့စျေး အလိုအလျောက်တွက်ချက်ခြင်း
                            
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
        print(f"Skipping {cat_name} due to Cloudflare/Timeout: {e}")
        await page.close()
        return []

async def main():
    async with async_playwright() as p:
        # GitHub Actions စနစ်နှင့် ကိုက်ညီမည့် အကောင်းဆုံး Browser Arguments များ
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
        
        # လူသုံးအများဆုံး Screen Size နှင့် User Agent ကို ပုံဖော်ခြင်း
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        # ဆေးဝါး၊ အိမ်သုံး၊ မိဖိုချောင်သုံး အပါအဝင် ရှိသမျှ အမျိုးအစားစုံလင်လှသော ကဏ္ဍကြီးများ
        categories = {
            "health_medicine_beauty": "https://www.shop.com.mm/health-beauty/",
            "home_kitchen_lifestyle": "https://www.shop.com.mm/home-lifestyle/",
            "electronic_devices": "https://www.shop.com.mm/electronic-devices/",
            "groceries_supermarket": "https://www.shop.com.mm/groceries-shop/",
            "men_fashion": "https://www.shop.com.mm/mens-fashion/",
            "women_fashion": "https://www.shop.com.mm/womens-fashion/"
        }

        print(f"Initializing Mega Anti-Block Scraper Bot for {len(categories)} Categories...")

        for cat_name, url in categories.items():
            products = await scrape_site_category(context, cat_name, url)
            if products:
                save_product_data(cat_name, products)
            # အပိတ်မခံရစေရန် တစ်ခုပြီးတစ်ခုကြား ၆ စက္ကန့် အနားပေးခြင်း
            await asyncio.sleep(6)
                
        await browser.close()

if name == "main":
    asyncio.run(main())
