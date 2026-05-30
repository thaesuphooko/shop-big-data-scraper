import os
import json
import re

def generate_smart_products(cat_name):
    """
    သီစုလုပ်ငန်းအတွက် အချက်အလက်များကို GitHub Server ပေါ်တွင် တိုက်ရိုက် အလိုအလျောက် ထုတ်လုပ်ပေးသည့် စနစ်
    """
    base_items = {
        "just_for_you": [
            {"title": "Premium Multi-Purpose Daily Organizer", "price": 18500, "img": "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=200"},
            {"title": "Trending Smart Digital Watch Series 9", "price": 45000, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=200"},
            {"title": "Mini Portable Bluetooth Speaker Bass Pro", "price": 28000, "img": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?q=80&w=200"}
        ],
        "health_and_beauty": [
            {"title": "Organic Aloe Vera Soothing Gel (300ml)", "price": 8500, "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=200"},
            {"title": "Hydrating Hyaluronic Acid Facial Serum", "price": 24000, "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=200"},
            {"title": "Premium Sunscreen SPF 50+ PA++++", "price": 19500, "img": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?q=80&w=200"}
        ],
        "tv_and_home_appliances": [
            {"title": "Smart Electric Inverter Kettle 2.0L", "price": 35000, "img": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?q=80&w=200"},
            {"title": "Mini Desktop Air Purifier with HEPA Filter", "price": 68000, "img": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?q=80&w=200"},
            {"title": "High-Speed Handheld Garment Steamer", "price": 42000, "img": "https://images.unsplash.com/photo-1525857597365-5f6dbff2e36e?q=80&w=200"}
        ],
        "groceries_and_pets": [
            {"title": "Premium Roasted Arabica Coffee Beans (500g)", "price": 16500, "img": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?q=80&w=200"},
            {"title": "Organic Chia Seeds Superfood (250g)", "price": 9800, "img": "https://images.unsplash.com/photo-1515543904379-3d757afe72e2?q=80&w=200"},
            {"title": "Nutritious Salmon Pet Treats for Cats & Dogs", "price": 7500, "img": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?q=80&w=200"}
        ],
        "babies_and_toys": [
            {"title": "Educational Wooden Building Blocks Set", "price": 18000, "img": "https://images.unsplash.com/photo-1515488042361-404e9250afef?q=80&w=200"},
            {"title": "Soft Cotton Anti-Slip Baby Socks (3 Pairs)", "price": 5500, "img": "https://images.unsplash.com/photo-1540479859555-17af45c78602?q=80&w=200"},
            {"title": "Cute Plush Animal Squishy Toy Pack", "price": 12500, "img": "https://images.unsplash.com/photo-1559251606-c623743a6d76?q=80&w=200"}
        ],
        "electronic_devices": [
            {"title": "Dual-Port Fast Charging Power Bank 20000mAh", "price": 38000, "img": "https://images.unsplash.com/photo-1609592424109-dd9892f1b177?q=80&w=200"},
            {"title": "Wireless Ergonomic Silent Optical Mouse", "price": 15000, "img": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?q=80&w=200"},
            {"title": "HD Clear Waterproof Action Camera", "price": 75000, "img": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?q=80&w=200"}
        ],
        "electronic_accessories": [
            {"title": "Premium Braided Type-C Fast Cable (2m)", "price": 6500, "img": "https://images.unsplash.com/photo-1543269664-76bc3997d9ea?q=80&w=200"},
            {"title": "Universal Travel Adapter with Surge Protection", "price": 14500, "img": "https://images.unsplash.com/photo-1563770660941-20978e870e26?q=80&w=200"},
            {"title": "Adjustable Desktop Phone and Tablet Stand", "price": 8500, "img": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?q=80&w=200"}

],
        "womens_fashion": [
            {"title": "Elegant Vintage Linen Summer Dress", "price": 28000, "img": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=200"},
            {"title": "Classic Leather Crossbody Shoulder Bag", "price": 35000, "img": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=200"},
            {"title": "Comfy Pastel Canvas Sneakers", "price": 26000, "img": "https://images.unsplash.com/photo-1560343090-f0409e92791a?q=80&w=200"}
        ],
        "home_and_lifestyle": [
            {"title": "Nordic Style Ceramic Flower Vase", "price": 16000, "img": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?q=80&w=200"},
            {"title": "Aromatic Lavender Scented Soy Candle", "price": 9500, "img": "https://images.unsplash.com/photo-1603006905003-be475563bc59?q=80&w=200"},
            {"title": "Stainless Steel Insulated Tumbler (500ml)", "price": 14000, "img": "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?q=80&w=200"}
        ],
        "watches_and_accessories": [
            {"title": "Minimalist Quartz Watch with Leather Strap", "price": 32000, "img": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=200"},
            {"title": "Classic Aviator Polarized Sunglasses", "price": 18500, "img": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=200"},
            {"title": "Luxury Stainless Steel Cuff Bracelet", "price": 12000, "img": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?q=80&w=200"}
        ],
        "mens_fashion": [
            {"title": "Premium Slim Fit Cotton Oxford Shirt", "price": 24000, "img": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?q=80&w=200"},
            {"title": "Casual Stretch Chino Pants", "price": 29000, "img": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?q=80&w=200"},
            {"title": "Classic Leather Minimalist Wallet", "price": 15000, "img": "https://images.unsplash.com/photo-1627123424574-724758594e93?q=80&w=200"}
        ]
    }

    products = []
    items_to_use = base_items.get(cat_name, base_items["just_for_you"])
    
    # ပစ္စည်းအစုံအလင်ဖြစ်အောင် ပတ်ပြီး ဒေတာတိုးပွားစေခြင်း (၅၅% Discount ပါတွက်ပြီးသား)
    for i in range(1, 151):
        template = items_to_use[(i - 1) % len(items_to_use)]
        orig_price = template["price"] + (i * 100)
        disc_price = int(orig_price * 0.45)
        
        products.append({
            "title": f"{template['title']} (Batch #{i:03d})",
            "image": template["img"],
            "original_price": f"Ks {orig_price:,}",
            "discount_price": f"Ks {disc_price:,}",
            "status": "In Stock"
        })
    return products

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
    print(f" Successfully generated {len(products)} products in {folder_path}")

def main():
    categories = [
        "just_for_you", "health_and_beauty", "tv_and_home_appliances",
        "groceries_and_pets", "babies_and_toys", "electronic_devices",
        "electronic_accessories", "womens_fashion", "home_and_lifestyle",
        "watches_and_accessories", "mens_fashion"
    ]
    
    print(f"Starting Automated Static Data Generator Engine...")
    
    for cat_name in categories:
        products = generate_smart_products(cat_name)
        save_product_data(cat_name, products)

if name == "main":
    main()
