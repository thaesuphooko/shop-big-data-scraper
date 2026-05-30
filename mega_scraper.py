categories = await page.evaluate('''() => {
                const links = document.querySelectorAll('a');
                const catMap = {};
                links.forEach(link => {
                    const href = link.href;
                    const text = link.innerText ? link.innerText.trim() : "";
                    if (href && (href.includes('/electronic-devices/')  href.includes('/groceries/')  href.includes('/health-beauty/')  href.includes('/home-lifestyle/')  href.includes('.shop.com.mm/'))) {
                        if (text && text.length > 2 && text.length < 30) {
                            catMap[text] = href;
                        }
                    }
                });
                return catMap;
            }''')
        except Exception as e:
            print(f"Failed to load homepage menu: {e}")
            categories = {}
            
        await page.close()

        if not categories or len(categories) < 5:
            categories = {
                "health_medicine_beauty": "https://www.shop.com.mm/health-beauty/",
                "home_kitchen_lifestyle": "https://www.shop.com.mm/home-lifestyle/",
                "electronic_devices": "https://www.shop.com.mm/electronic-devices/",
                "groceries_supermarket": "https://www.shop.com.mm/groceries-shop/",
                "men_fashion": "https://www.shop.com.mm/mens-fashion/",
                "women_fashion": "https://www.shop.com.mm/womens-fashion/"
            }

        print(f"Found {len(categories)} categories to scrape! Starting Mega Process...")

        for cat_name, url in categories.items():
            products = await scrape_site_category(context, cat_name, url)
            if products:
                save_product_data(cat_name, products)
                
        await browser.close()

if name == "main":
    asyncio.run(main())
