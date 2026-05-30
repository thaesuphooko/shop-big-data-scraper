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
        
    chunk_size = 500
    for i in range(0, len(products), chunk_size):
        page_num = (i // chunk_size) + 1
        chunk = products[i:i + chunk_size]
        
        file_path = f"{folder_path}/page_{page_num}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=4)
    print(f"=== Successfully Saved {len(products)} products to {folder_path} ===")

async def scrape_mobile_tab(context, cat_name, url):
    print(f"Scraping Mobile Tab: {cat_name} -> {url}")
    page = await context.new_page()
    
    # Automation Tags များအားလုံးကို ဖုံးကွယ်ပြီး ဖုန်း Browser အစစ်အတိုင်း ပြုလုပ်ခြင်း
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    products_data = []
    try:
        # Mobile Page သို့ သွားခြင်း
        await page.goto(url, wait_until="commit", timeout=90000)
        await asyncio.sleep(random.uniform(4, 6))
        
        # စာမျက်နှာအောက်ခြေထိ ရောက်အောင် ဖြည်းဖြည်းချင်း အကြိမ်များစွာ ဆွဲချခြင်း
        for _ in range(15):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(random.uniform(1.5, 2.5))
            
        # HTML ဖွဲ့စည်းပုံအမျိုးမျိုးမှ Product Data များကို သိမ်းကျုံးရှာဖွေခြင်း
        products_data = await page.evaluate('''() => {
            const list = [];
            
            // နည်းလမ်း (၁) - Shop Mobile App JSON Data ဝင်နေပါက တိုက်ရိုက်ယူခြင်း
            if (window.moduleData) {
                try {
                    const modules = window.moduleData.data.modules || [];
                    modules.forEach(m => {
                        const items = m.data.list  m.data.products  [];
                        items.forEach(p => {
                            if (p.name || p.title) {
                                list.push({
                                    title: p.name || p.title,
                                    image: p.image  p.imgUrl  "",
                                    price: p.price  p.priceShow  ""
                                });
                            }
                        });
                    });
                } catch(e){}
            }
            
            // နည်းလမ်း (၂) - မိုဘိုင်း ဝက်ဘ်ဆိုက် Element များထဲမှ ရှာဖွေခြင်း
            const selectors = [
                '.card-jfy-item', '.hp-mod-card-item', '[data-qa-locator="product-item"]',
                '.product-item', '.item-card', '.c1_MzI', '.c2Pr2Y'
            ];
            
            let items = [];
            selectors.forEach(sel => {
                if (items.length === 0) items = document.querySelectorAll(sel);
            });
            
            items.forEach(item => {
                try {
                    const titleEl = item.querySelector('.card-jfy-title')  item.querySelector('.title')  item.querySelector('.hp-mod-card-item-title') || item.querySelector('.c1A2ss');
                    const priceEl = item.querySelector('.hp-mod-price')  item.querySelector('.price')  item.querySelector('.c3gUW0');
                    const imgEl = item.querySelector('img');
                    
                    if (titleEl && priceEl) {
                        list.push({
                            title: titleEl.innerText.trim(),
                            image: imgEl ? imgEl.src : "",
                            price: priceEl.innerText.trim()

});
                    }
                } catch(e){}
            });
            return list;
        }''')
        
    except Exception as e:
        print(f"Error scraping {cat_name}: {e}")
    finally:
        await page.close()
        
    # စျေးနှုန်းများကို ကျပ်ငွေအဖြစ် ပြောင်းလဲပြီး ၅၅% လျှော့စျေး (Discount) အလိုအလျောက် တွက်ချက်ခြင်း
    final_products = []
    for p in products_data:
        try:
            raw_price = re.sub(r'[^0-9]', '', p['price'])
            if raw_price:
                original_price = int(raw_price)
                if original_price > 0:
                    discount_price = int(original_price * 0.45)
                    final_products.append({
                        "title": p['title'],
                        "image": p['image'],
                        "original_price": f"Ks {original_price:,}",
                        "discount_price": f"Ks {discount_price:,}",
                        "status": "In Stock"
                    })
        except:
            continue
            
    return final_products

async def main():
    async with async_playwright() as p:
        # GitHub Actions တွင် လုံးဝ အမှားကင်းစေမည့် Chromium Setup
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        # မိုဘိုင်းဖုန်းဖြင့် ဝင်ရောက်နေသကဲ့သို့ ပုံဖော်ပေးခြင်း (Mobile Viewport)
        context = await browser.new_context(
            viewport={'width': 412, 'height': 915},
            user_agent="Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            is_mobile=True,
            has_touch=True
        )
        
        # သီစုပြထားသော ဘယ်ဘက်ဘေးက Tab လမ်းကြောင်းများ အားလုံး စုံလင်စွာ ထည့်သွင်းထားခြင်း
        mobile_tabs = {
            "just_for_you": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/just-for-you",
            "health_and_beauty": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/health-beauty",
            "tv_and_home_appliances": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/tv-home-appliances",
            "groceries_and_pets": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/groceries-pets",
            "babies_and_toys": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/babies-toys",
            "electronic_devices": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/electronic-devices",
            "electronic_accessories": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/electronic-accessories",
            "womens_fashion": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/womens-fashion",
            "home_and_lifestyle": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/home-lifestyle",
            "watches_and_accessories": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/watches-accessories",
            "mens_fashion": "https://pages.shop.com.mm/wow/gcp/shop/channel/mm/main/mens-fashion"
        }

        print(f"Starting Scraper Bot for {len(mobile_tabs)} Mobile Tabs...")

        for cat_name, url in mobile_tabs.items():
            products = await scrape_mobile_tab(context, cat_name, url)
            if products:
                save_product_data(cat_name, products)
            await asyncio.sleep(random.uniform(4, 7)) # ကာကွယ်ရေးစနစ် ကျော်ရန် နားပေးခြင်း
                
        await browser.close()

if name == "main":
    asyncio.run(main())
