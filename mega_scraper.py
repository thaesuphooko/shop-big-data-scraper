import asyncio
from playwright.async_api import async_playwright
import json
import os

def save_product_data(category, products):
    folder_path = f"data/{category}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    chunk_size = 1000
    for i in range(0, len(products), chunk_size):
        page_num = (i // chunk_size) + 1
        chunk = products[i:i + chunk_size]
        
        file_path = f"{folder_path}/page_{page_num}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(chunk)} products to {file_path}")

async def scrape_category(context, cat_name, url):
    print(f"Scraping category: {cat_name} via Playwright...")
    page = await context.new_page()
    
    # လူအစစ်လိုမျိုး ဟန်ဆောင်ပြီး Website သို့ ဝင်ခြင်း
    await page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    try {
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # ဖုန်းနဲ့ ကွန်ပျူတာ Screen အလိုက် ပစ္စည်းတွေအကုန်ပေါ်အောင် အောက်သို့ Scroll ဆွဲချခြင်း
        for _ in range(5):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(1)

        # Website ပေါ်က ပစ္စည်းအချက်အလက်များကို ဆွဲထုတ်ခြင်း
        products_data = await page.evaluate('''() => {
            const items = document.querySelectorAll('.card-jfy-item') || document.querySelectorAll('.hp-mod-card-item');
            const data = [];
            items.forEach(item => {
                try {
                    const title = item.querySelector('.card-jfy-title')?.innerText || item.querySelector('.hp-mod-card-item-title')?.innerText;
                    const image = item.querySelector('img')?.src;
                    const priceText = item.querySelector('.hp-mod-price')?.innerText;
                    
                    if (title && priceText) {
                        const originalPrice = parseInt(priceText.replace(/[^0-0]/g, ''));
                        const discountPrice = Math.floor(originalPrice * 0.45); // ၅၅% လျှော့စျေးတွက်ခြင်း
                        
                        data.push({
                            title: title.trim(),
                            image: image,
                            original_price: "Ks " + originalPrice.toLocaleString(),
                            discount_price: "Ks " + discountPrice.toLocaleString()
                        });
                    }
                } catch (e) {}
            });
            return data;
        }''')
        
        await page.close()
        return products_data
    except Exception as e:
        print(f"Error scraping {cat_name}: {e}")
        await page.close()
        return []

async def main():
    target_categories = {
        "electronic_devices": "https://www.shop.com.mm/electronic-devices/",
        "men_fashion": "https://www.shop.com.mm/mens-fashion/",
        "women_fashion": "https://www.shop.com.mm/womens-fashion/"
    }

    async with async_playwright() as p:
        # Browser အစစ်ကြီးကို နောက်ကွယ်မှာ ခေါ်ဖွင့်လိုက်ခြင်း
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        for cat_name, url in target_categories.items():
            products = await scrape_category(context, cat_name, url)
            if products:
                save_product_data(cat_name, products)
                
        await browser.close()

if name == "main":
    asyncio.run(main())
