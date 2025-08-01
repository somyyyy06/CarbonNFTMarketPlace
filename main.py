
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import hashlib
from datetime import datetime, timedelta
import uuid
import random

app = Flask(__name__)
app.secret_key = 'walmart_ecomart_nft_secret_key'

# Mock database for demonstration
users_db = {}
purchases_db = []
nft_badges_db = {}
cart_db = {}
wishlist_db = {}
accounts_db = {
    'demo@walmart.com': {
        'password': 'demo123',
        'name': 'Demo User',
        'phone': '+1234567890',
        'address': '123 Main St, City, State 12345'
    }
}

# NFT Badge tiers and requirements
NFT_TIERS = {
    'green_starter': {'name': 'Green Starter', 'co2_required': 10, 'color': '#28a745'},
    'eco_warrior': {'name': 'Eco Warrior', 'co2_required': 50, 'color': '#fd7e14'},
    'planet_protector': {'name': 'Planet Protector', 'co2_required': 100, 'color': '#6c757d'},
    'climate_champion': {'name': 'Climate Champion', 'co2_required': 200, 'color': '#6f42c1'},
    'earth_guardian': {'name': 'Earth Guardian', 'co2_required': 500, 'color': '#20c997'}
}

# Comprehensive product catalog
REGULAR_PRODUCTS = [
    {'id': 1, 'name': 'Regular Cotton T-Shirt', 'price': 15.99, 'original_price': 20.00, 'discount': 25, 'rating': 4.2, 'reviews': 125, 'category': 'clothing', 'image': '/static/products/regularCottonT-shirt.png'},
    {'id': 2, 'name': 'Standard Smartphone', 'price': 46000, 'original_price': 55000, 'discount': 16, 'rating': 4.3, 'reviews': 892, 'category': 'electronics', 'image': '/static/products/smartPhone.jpeg'},
    {'id': 3, 'name': 'Regular Jeans', 'price': 3800, 'original_price': 4500, 'discount': 15, 'rating': 4.1, 'reviews': 234, 'category': 'clothing', 'image': '/static/products/regularJeans.jpeg'},
    {'id': 4, 'name': 'Leather Jacket', 'price': 200, 'original_price': 200, 'discount': 0, 'rating': 4.5, 'reviews': 87, 'category': 'clothing', 'image': '/static/products/leatherjacket.png'},
    {'id': 5, 'name': 'Gaming Laptop', 'price': 89999, 'original_price': 99999, 'discount': 10, 'rating': 4.7, 'reviews': 156, 'category': 'electronics', 'image': '/static/products/gamingLaptop.jpeg'},
    {'id': 6, 'name': 'Plastic Water Bottle', 'price': 12.99, 'original_price': 15.99, 'discount': 19, 'rating': 3.8, 'reviews': 67, 'category': 'lifestyle', 'image': '/static/products/waterBottle.jpg'},
    {'id': 7, 'name': 'Regular Sneakers', 'price': 5999, 'original_price': 6999, 'discount': 14, 'rating': 4.2, 'reviews': 298, 'category': 'footwear', 'image': '/static/products/sneakers.jpeg'},
    {'id': 8, 'name': 'Standard Backpack', 'price': 2999, 'original_price': 3499, 'discount': 14, 'rating': 4.0, 'reviews': 178, 'category': 'accessories', 'image': '/static/products/bagPack.jpeg'},
] + [
    {'id': i+9, 'name': f'Product {i+9}', 'price': random.randint(500, 50000), 'original_price': random.randint(600, 60000), 'discount': random.randint(5, 30), 'rating': round(random.uniform(3.5, 4.8), 1), 'reviews': random.randint(50, 500), 'category': random.choice(['electronics', 'clothing', 'home', 'beauty', 'sports']), 'image': f'/static/products/Product{i+9}.jpg'}
    for i in range(42)  # Generate 42 more products for a total of 50
]

ECO_PRODUCTS = [
    {'id': 101, 'name': 'Organic Cotton T-Shirt', 'price': 18.99, 'co2_saved': 8.2, 'category': 'clothing', 'tags': ['Organic Cotton', 'Fair Trade', 'Carbon Neutral Shipping'], 'industry_avg': 18.2, 'image': '/static/eco_prod/organicTshirt.jpeg', 'rating': 4.6, 'reviews': 234},
    {'id': 102, 'name': 'Eco-Friendly Smartphone', 'price': 649.99, 'co2_saved': 45.6, 'category': 'electronics', 'tags': ['Recycled Materials', 'Renewable Energy Manufacturing', 'Biodegradable Packaging'], 'industry_avg': 89.7, 'image': '/static/eco_prod/eco_smartPhone.jpg', 'rating': 4.4, 'reviews': 156},
    {'id': 103, 'name': 'Sustainable Jeans', 'price': 69.99, 'co2_saved': 12.1, 'category': 'clothing', 'tags': ['Recycled Denim', 'Water Efficient Production', 'Plastic Free Packaging'], 'industry_avg': 35.8, 'image': '/static/eco_prod/eco_jeans.jpeg', 'rating': 4.5, 'reviews': 89},
    {'id': 104, 'name': 'Solar Power Bank', 'price': 39.99, 'co2_saved': 10.0, 'category': 'electronics', 'tags': ['Solar Powered', 'Recycled Materials'], 'industry_avg': 15.2, 'image': '/static/eco_prod/eco_powerBank.png', 'rating': 4.3, 'reviews': 178},
    {'id': 105, 'name': 'Bamboo Toothbrush Set', 'price': 12.99, 'co2_saved': 44.1, 'category': 'personal_care', 'tags': ['Bamboo', 'Biodegradable'], 'industry_avg': 89.7, 'image': '/static/eco_prod/eco_toothbrush.jpg', 'rating': 4.7, 'reviews': 267},
    {'id': 106, 'name': 'Recycled Plastic Jacket', 'price': 159.99, 'co2_saved': 23.7, 'category': 'clothing', 'tags': ['Recycled Plastic', 'Waterproof'], 'industry_avg': 45.9, 'image': '/static/eco_prod/eco_jacket.jpg', 'rating': 4.2, 'reviews': 134},
    {'id': 107, 'name': 'Reusable Stainless Steel Water Bottle', 'price': 24.99, 'co2_saved': 15.3, 'category': 'lifestyle', 'tags': ['Stainless Steel', 'BPA Free', 'Lifetime Guarantee'], 'industry_avg': 8.7, 'image': '/static/eco_prod/eco_bottle.jpg', 'rating': 4.8, 'reviews': 423},
    {'id': 108, 'name': 'Hemp Fiber Backpack', 'price': 79.99, 'co2_saved': 18.9, 'category': 'accessories', 'tags': ['Hemp Fiber', 'Durable', 'Biodegradable'], 'industry_avg': 12.4, 'image': '/static/eco_prod/eco_backpack.jpeg', 'rating': 4.4, 'reviews': 198},
    {'id': 109, 'name': 'LED Light Bulbs (4-pack)', 'price': 12.99, 'co2_saved': 8.7, 'category': 'home', 'tags': ['Energy Efficient', 'Long Lasting'], 'industry_avg': 4.2, 'image': '/static/eco_prod/eco_bulb.jpeg', 'rating': 4.6, 'reviews': 567},
    {'id': 110, 'name': 'Recycled Paper Towels', 'price': 8.49, 'co2_saved': 1.2, 'category': 'household', 'tags': ['Recycled Paper', 'Compostable'], 'industry_avg': 2.1, 'image': '/static/eco_prod/eco_towels.jpeg', 'rating': 4.1, 'reviews': 298},
] + [
    {'id': i+111, 'name': f'Eco Product {i+11}', 'price': round(random.uniform(9.99, 199.99), 2), 'co2_saved': round(random.uniform(1.0, 50.0), 1), 'category': random.choice(['clothing', 'electronics', 'home', 'personal_care', 'lifestyle']), 'tags': random.sample(['Organic', 'Recycled', 'Biodegradable', 'Solar Powered', 'Carbon Neutral'], 2), 'industry_avg': round(random.uniform(5.0, 60.0), 1), 'image': f'/static/eco_prod/Product{i+11}.jpeg', 'rating': round(random.uniform(4.0, 4.9), 1), 'reviews': random.randint(50, 400)}
    for i in range(40)  # Generate 40 more eco products for a total of 50
]

def get_user_data(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            'total_co2_saved': 0,
            'monthly_co2_saved': 0,
            'eco_products_purchased': 0,
            'monthly_goal': 50,
            'eco_products_goal': 20,
            'last_reset': datetime.now().replace(day=1),
            'nft_badges': [],
            'total_spent': 0,
            'total_products': 0
        }
    return users_db[user_id]

def get_cart(user_id):
    if user_id not in cart_db:
        cart_db[user_id] = []
    return cart_db[user_id]

def get_wishlist(user_id):
    if user_id not in wishlist_db:
        wishlist_db[user_id] = []
    return wishlist_db[user_id]

def check_monthly_reset(user_data):
    current_month = datetime.now().replace(day=1)
    if user_data['last_reset'] < current_month:
        user_data['monthly_co2_saved'] = 0
        user_data['eco_products_purchased'] = 0
        user_data['last_reset'] = current_month

def check_and_award_nft_badges(user_id, user_data):
    awarded_badges = []
    total_co2 = user_data['total_co2_saved']
    
    for tier_id, tier_info in NFT_TIERS.items():
        if total_co2 >= tier_info['co2_required'] and tier_id not in user_data['nft_badges']:
            nft_id = str(uuid.uuid4())
            badge_data = {
                'id': nft_id,
                'tier': tier_id,
                'name': tier_info['name'],
                'co2_saved': total_co2,
                'earned_date': datetime.now().isoformat(),
                'owner': user_id,
                'minted': False,
                'metadata': {
                    'description': f'NFT Badge for saving {tier_info["co2_required"]}+ kg CO2',
                    'image_url': f'/static/images/badges/{tier_id}.png',
                    'attributes': [
                        {'trait_type': 'CO2 Saved', 'value': f'{total_co2} kg'},
                        {'trait_type': 'Tier', 'value': tier_info['name']},
                        {'trait_type': 'Earned Date', 'value': datetime.now().strftime('%Y-%m-%d')}
                    ]
                }
            }
            
            user_data['nft_badges'].append(tier_id)
            nft_badges_db[nft_id] = badge_data
            awarded_badges.append(badge_data)
    
    return awarded_badges

@app.route('/')
def index():
    user_id = session.get('user_id', 'demo_user')
    session['user_id'] = user_id
    user_data = get_user_data(user_id)
    check_monthly_reset(user_data)
    cart = get_cart(user_id)
    
    featured_products = REGULAR_PRODUCTS[:12]
    featured_eco_products = ECO_PRODUCTS[:6]
    
    wishlist = get_wishlist(user_id)
    
    return render_template('index.html', 
                         user_data=user_data, 
                         featured_products=featured_products,
                         featured_eco_products=featured_eco_products,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist))

@app.route('/ecoproducts')
def ecoproducts():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    products = ECO_PRODUCTS[start_idx:end_idx]
    has_next = end_idx < len(ECO_PRODUCTS)
    has_prev = page > 1
    
    return render_template('ecoproducts.html', 
                         eco_products=products,
                         user_data=user_data,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist),
                         page=page,
                         has_next=has_next,
                         has_prev=has_prev)

@app.route('/rewards')
def rewards():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    check_monthly_reset(user_data)
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    # Get user's NFT badges
    user_nft_badges = []
    for badge_id, badge_data in nft_badges_db.items():
        if badge_data['tier'] in user_data['nft_badges']:
            user_nft_badges.append(badge_data)
    
    # Calculate progress for each tier
    tier_progress = {}
    total_co2 = user_data['total_co2_saved']
    
    for tier_id, tier_info in NFT_TIERS.items():
        earned = tier_id in user_data['nft_badges']
        if earned:
            progress = 100
            remaining = 0
        else:
            progress = min(100, (total_co2 / tier_info['co2_required']) * 100)
            remaining = max(0, tier_info['co2_required'] - total_co2)
        
        tier_progress[tier_id] = {
            'progress': progress,
            'remaining': remaining,
            'earned': earned,
            **tier_info
        }
    
    return render_template('rewards.html', 
                         user_data=user_data, 
                         tier_progress=tier_progress,
                         user_nft_badges=user_nft_badges,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist))

@app.route('/nft-marketplace')
def nft_marketplace():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    # Get all minted NFTs for marketplace
    marketplace_nfts = []
    for badge_id, badge_data in nft_badges_db.items():
        if badge_data.get('minted'):
            marketplace_nfts.append(badge_data)
    
    return render_template('nft_marketplace.html',
                         user_data=user_data,
                         marketplace_nfts=marketplace_nfts,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist))

@app.route('/cart')
def cart():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart_items = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    # Get full product details for cart items
    cart_details = []
    total_price = 0
    total_co2_saved = 0
    
    for item in cart_items:
        if item['type'] == 'eco':
            product = next((p for p in ECO_PRODUCTS if p['id'] == item['id']), None)
            if product:
                item_total = product['price'] * item['quantity']
                total_price += item_total
                total_co2_saved += product['co2_saved'] * item['quantity']
                cart_details.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'total': item_total,
                    'type': 'eco'
                })
        else:
            product = next((p for p in REGULAR_PRODUCTS if p['id'] == item['id']), None)
            if product:
                item_total = product['price'] * item['quantity']
                total_price += item_total
                cart_details.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'total': item_total,
                    'type': 'regular'
                })
    
    return render_template('cart.html',
                         user_data=user_data,
                         cart_items=cart_details,
                         cart_count=len(cart_items),
                         wishlist_count=len(wishlist),
                         total_price=total_price,
                         total_co2_saved=total_co2_saved)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user_id = session.get('user_id', 'demo_user')
    data = request.json
    product_id = data.get('product_id')
    product_type = data.get('type', 'regular')  # 'regular' or 'eco'
    quantity = data.get('quantity', 1)
    
    cart = get_cart(user_id)
    
    # Check if item already in cart
    existing_item = next((item for item in cart if item['id'] == product_id and item['type'] == product_type), None)
    
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        cart.append({
            'id': product_id,
            'type': product_type,
            'quantity': quantity
        })
    
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/purchase', methods=['POST'])
def purchase():
    user_id = session.get('user_id', 'demo_user')
    data = request.json
    
    if 'cart_checkout' in data:
        # Checkout entire cart
        cart_items = get_cart(user_id)
        user_data = get_user_data(user_id)
        check_monthly_reset(user_data)
        
        total_co2_saved = 0
        total_spent = 0
        new_badges = []
        
        for item in cart_items:
            if item['type'] == 'eco':
                product = next((p for p in ECO_PRODUCTS if p['id'] == item['id']), None)
                if product:
                    co2_saved = product['co2_saved'] * item['quantity']
                    price = product['price'] * item['quantity']
                    
                    user_data['total_co2_saved'] += co2_saved
                    user_data['monthly_co2_saved'] += co2_saved
                    user_data['eco_products_purchased'] += item['quantity']
                    user_data['total_spent'] += price
                    user_data['total_products'] += item['quantity']
                    
                    total_co2_saved += co2_saved
                    total_spent += price
                    
                    # Record each item purchase
                    for _ in range(item['quantity']):
                        purchase_record = {
                            'id': len(purchases_db) + 1,
                            'user_id': user_id,
                            'product': product,
                            'timestamp': datetime.now().isoformat(),
                            'co2_saved': product['co2_saved'],
                            'type': 'eco',
                            'status': 'delivered'
                        }
                        purchases_db.append(purchase_record)
            else:
                product = next((p for p in REGULAR_PRODUCTS if p['id'] == item['id']), None)
                if product:
                    price = product['price'] * item['quantity']
                    user_data['total_spent'] += price
                    user_data['total_products'] += item['quantity']
                    total_spent += price
                    
                    # Record each item purchase
                    for _ in range(item['quantity']):
                        purchase_record = {
                            'id': len(purchases_db) + 1,
                            'user_id': user_id,
                            'product': product,
                            'timestamp': datetime.now().isoformat(),
                            'co2_saved': 0,
                            'type': 'regular',
                            'status': 'delivered'
                        }
                        purchases_db.append(purchase_record)
        
        # Check for new NFT badges
        if total_co2_saved > 0:
            new_badges = check_and_award_nft_badges(user_id, user_data)
        
        # Clear cart
        cart_db[user_id] = []
        
        return jsonify({
            'success': True,
            'co2_saved': total_co2_saved,
            'total_co2_saved': user_data['total_co2_saved'],
            'total_spent': total_spent,
            'new_badges': new_badges
        })
    
    else:
        # Single product purchase
        product_id = int(data.get('product_id'))
        product_type = data.get('type', 'eco')
        
        if product_type == 'eco':
            product = next((p for p in ECO_PRODUCTS if p['id'] == product_id), None)
        else:
            product = next((p for p in REGULAR_PRODUCTS if p['id'] == product_id), None)
            
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'})
        
        user_data = get_user_data(user_id)
        check_monthly_reset(user_data)
        
        user_data['total_spent'] += product['price']
        user_data['total_products'] += 1
        
        new_badges = []
        co2_saved = 0
        
        if product_type == 'eco':
            co2_saved = product['co2_saved']
            user_data['total_co2_saved'] += co2_saved
            user_data['monthly_co2_saved'] += co2_saved
            user_data['eco_products_purchased'] += 1
            
            # Check for new NFT badges
            new_badges = check_and_award_nft_badges(user_id, user_data)
        
        # Record purchase
        purchase_record = {
            'id': len(purchases_db) + 1,
            'user_id': user_id,
            'product': product,
            'timestamp': datetime.now().isoformat(),
            'co2_saved': co2_saved,
            'type': product_type,
            'status': 'delivered'
        }
        purchases_db.append(purchase_record)
        
        return jsonify({
            'success': True,
            'co2_saved': co2_saved,
            'total_co2_saved': user_data['total_co2_saved'],
            'new_badges': new_badges
        })

@app.route('/mint_nft', methods=['POST'])
def mint_nft():
    user_id = session.get('user_id', 'demo_user')
    badge_id = request.json.get('badge_id')
    wallet_address = request.json.get('wallet_address')
    is_tier_id = request.json.get('is_tier_id', False)
    
    user_data = get_user_data(user_id)
    
    # If it's a tier ID, find or create the badge
    if is_tier_id and badge_id in NFT_TIERS:
        tier_info = NFT_TIERS[badge_id]
        
        # Check if user has earned this tier
        if badge_id not in user_data['nft_badges']:
            return jsonify({'success': False, 'message': 'Badge not earned yet'})
        
        # Find existing badge or create new one
        existing_badge = None
        for nft_id, badge_data in nft_badges_db.items():
            if badge_data['tier'] == badge_id and badge_data.get('owner') == user_id:
                existing_badge = badge_data
                existing_badge['id'] = nft_id
                break
        
        if not existing_badge:
            # Create new badge
            nft_id = str(uuid.uuid4())
            badge_data = {
                'id': nft_id,
                'tier': badge_id,
                'name': tier_info['name'],
                'co2_saved': user_data['total_co2_saved'],
                'earned_date': datetime.now().isoformat(),
                'owner': user_id,
                'metadata': {
                    'description': f'NFT Badge for saving {tier_info["co2_required"]}+ kg CO2',
                    'image_url': f'/static/badges/{badge_id}.png',
                    'attributes': [
                        {'trait_type': 'CO2 Saved', 'value': f'{user_data["total_co2_saved"]} kg'},
                        {'trait_type': 'Tier', 'value': tier_info['name']},
                        {'trait_type': 'Earned Date', 'value': datetime.now().strftime('%Y-%m-%d')}
                    ]
                }
            }
            nft_badges_db[nft_id] = badge_data
        else:
            badge_data = existing_badge
    else:
        # Handle regular badge ID
        if badge_id not in nft_badges_db:
            return jsonify({'success': False, 'message': 'Badge not found'})
        
        badge_data = nft_badges_db[badge_id]
    
    # Check if already minted
    if badge_data.get('minted'):
        return jsonify({'success': False, 'message': 'Badge already minted'})
    
    # Prepare badge for minting
    badge_data['prepared_for_minting'] = True
    badge_data['wallet_address'] = wallet_address
    badge_data['prepare_date'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'badge': badge_data
    })

@app.route('/update_nft_transaction', methods=['POST'])
def update_nft_transaction():
    user_id = session.get('user_id', 'demo_user')
    badge_id = request.json.get('badge_id')
    transaction_hash = request.json.get('transaction_hash')
    wallet_address = request.json.get('wallet_address')
    
    if badge_id not in nft_badges_db:
        return jsonify({'success': False, 'message': 'Badge not found'})
    
    badge_data = nft_badges_db[badge_id]
    
    # Update with real blockchain transaction data
    badge_data['minted'] = True
    badge_data['mint_hash'] = transaction_hash
    badge_data['mint_date'] = datetime.now().isoformat()
    badge_data['owner'] = user_id
    badge_data['wallet_address'] = wallet_address
    badge_data['blockchain'] = 'Polygon'
    badge_data['network'] = 'mainnet'
    
    return jsonify({
        'success': True,
        'transaction_hash': transaction_hash,
        'badge': badge_data
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email in accounts_db and accounts_db[email]['password'] == password:
            session['user_id'] = email
            session['user_name'] = accounts_db[email]['name']
            session['logged_in'] = True
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'})
    
    user_id = session.get('user_id', 'demo_user')
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    return render_template('login.html', cart_count=len(cart), wishlist_count=len(wishlist))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        phone = data.get('phone', '')
        
        if email in accounts_db:
            return jsonify({'success': False, 'message': 'Email already exists'})
        
        accounts_db[email] = {
            'password': password,
            'name': name,
            'phone': phone,
            'address': ''
        }
        
        session['user_id'] = email
        session['user_name'] = name
        session['logged_in'] = True
        
        return jsonify({'success': True, 'message': 'Account created successfully'})
    
    user_id = session.get('user_id', 'demo_user')
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    return render_template('signup.html', cart_count=len(cart), wishlist_count=len(wishlist))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/account')
def account():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    account_info = accounts_db.get(user_id, {
        'name': 'Demo User',
        'phone': '',
        'address': ''
    })
    
    return render_template('account.html', 
                         user_data=user_data,
                         account_info=account_info,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist))

@app.route('/wishlist')
def wishlist():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart = get_cart(user_id)
    wishlist_items = get_wishlist(user_id)
    
    # Get full product details for wishlist items
    wishlist_details = []
    for item in wishlist_items:
        if item['type'] == 'eco':
            product = next((p for p in ECO_PRODUCTS if p['id'] == item['id']), None)
        else:
            product = next((p for p in REGULAR_PRODUCTS if p['id'] == item['id']), None)
        
        if product:
            wishlist_details.append({
                'product': product,
                'type': item['type']
            })
    
    return render_template('wishlist.html',
                         user_data=user_data,
                         wishlist_items=wishlist_details,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist_items))

@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    user_id = session.get('user_id', 'demo_user')
    data = request.json
    product_id = data.get('product_id')
    product_type = data.get('type', 'regular')
    
    wishlist = get_wishlist(user_id)
    
    # Check if item already in wishlist
    existing_item = next((item for item in wishlist if item['id'] == product_id and item['type'] == product_type), None)
    
    if not existing_item:
        wishlist.append({
            'id': product_id,
            'type': product_type
        })
        return jsonify({'success': True, 'wishlist_count': len(wishlist), 'message': 'Added to wishlist'})
    else:
        return jsonify({'success': False, 'message': 'Item already in wishlist'})

@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    user_id = session.get('user_id', 'demo_user')
    data = request.json
    product_id = data.get('product_id')
    product_type = data.get('type', 'regular')
    
    wishlist = get_wishlist(user_id)
    
    # Remove item from wishlist
    wishlist[:] = [item for item in wishlist if not (item['id'] == product_id and item['type'] == product_type)]
    
    return jsonify({'success': True, 'wishlist_count': len(wishlist)})

@app.route('/orders')
def orders():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    # Get user's purchase history
    user_orders = [purchase for purchase in purchases_db if purchase['user_id'] == user_id]
    
    return render_template('orders.html',
                         user_data=user_data,
                         orders=user_orders,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist))

@app.route('/returns')
def returns():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    # Get user's orders that can be returned (within 30 days and not already returned)
    returnable_orders = []
    for purchase in purchases_db:
        if purchase['user_id'] == user_id and purchase.get('status') == 'delivered':
            purchase_date = datetime.fromisoformat(purchase['timestamp'])
            days_since_purchase = (datetime.now() - purchase_date).days
            if days_since_purchase <= 30:
                purchase['days_left'] = max(0, 30 - days_since_purchase)
                returnable_orders.append(purchase)
    
    return render_template('returns.html',
                         user_data=user_data,
                         returnable_orders=returnable_orders,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist))

@app.route('/feedback')
def feedback():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    
    return render_template('feedback.html',
                         user_data=user_data,
                         cart_count=len(cart),
                         wishlist_count=len(wishlist))

@app.route('/api/user_stats')
def user_stats():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    check_monthly_reset(user_data)
    
    return jsonify(user_data)

@app.route('/api/user_badges')
def user_badges():
    user_id = session.get('user_id', 'demo_user')
    user_badges = []
    
    for badge_id, badge_data in nft_badges_db.items():
        if badge_data.get('owner') == user_id:
            user_badges.append(badge_data)
    
    return jsonify({'badges': user_badges})

@app.route('/api/cart_total')
def cart_total():
    user_id = session.get('user_id', 'demo_user')
    cart_items = get_cart(user_id)
    total_price = 0
    for item in cart_items:
        if item['type'] == 'eco':
            product = next((p for p in ECO_PRODUCTS if p['id'] == item['id']), None)
        else:
            product = next((p for p in REGULAR_PRODUCTS if p['id'] == item['id']), None)
        if product:
            total_price += product['price'] * item['quantity']
    return jsonify({'total_price': total_price})

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    user_id = session.get('user_id', 'demo_user')
    data = request.json
    
    feedback_record = {
        'id': len(purchases_db) + 1000,  # Offset to avoid ID conflicts
        'user_id': user_id,
        'order_id': data.get('order_id'),
        'name': data.get('name'),
        'email': data.get('email'),
        'feedback': data.get('feedback'),
        'rating': data.get('rating'),
        'timestamp': datetime.now().isoformat()
    }
    
    # You could store this in a feedback_db, but for demo purposes, we'll just acknowledge it
    return jsonify({'success': True, 'message': 'Feedback submitted successfully!'})

@app.route('/return_product', methods=['POST'])
def return_product():
    user_id = session.get('user_id', 'demo_user')
    data = request.json
    order_id = data.get('order_id')
    reason = data.get('reason')
    
    # Find the order
    order = next((purchase for purchase in purchases_db if purchase['id'] == order_id and purchase['user_id'] == user_id), None)
    
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'})
    
    # Check if return window is still open (30 days)
    purchase_date = datetime.fromisoformat(order['timestamp'])
    days_since_purchase = (datetime.now() - purchase_date).days
    
    if days_since_purchase > 30:
        return jsonify({'success': False, 'message': 'Return window has expired'})
    
    # Update order status
    order['status'] = 'returned'
    order['return_reason'] = reason
    order['return_date'] = datetime.now().isoformat()
    
    # Update user data (reverse the effects)
    user_data = get_user_data(user_id)
    user_data['total_spent'] -= order['product']['price']
    user_data['total_products'] -= 1
    
    if order['type'] == 'eco':
        user_data['total_co2_saved'] -= order['co2_saved']
        user_data['monthly_co2_saved'] -= order['co2_saved']
        user_data['eco_products_purchased'] -= 1
    
    return jsonify({'success': True, 'message': 'Return processed successfully!'})

# Add carbon helper data and route
CARBON_TIPS = {
    'transportation': [
        'Use public transport, walk, or bike instead of driving',
        'Consider carpooling or ride-sharing services',
        'Work from home when possible to reduce commuting',
        'Choose fuel-efficient or electric vehicles',
        'Combine errands into one trip',
        'Maintain your vehicle properly for better fuel efficiency'
    ],
    'energy': [
        'Switch to LED bulbs throughout your home',
        'Unplug electronics when not in use',
        'Use programmable thermostats',
        'Improve home insulation',
        'Consider renewable energy sources like solar panels',
        'Use energy-efficient appliances'
    ],
    'diet': [
        'Reduce meat consumption, especially beef',
        'Buy local and seasonal produce',
        'Minimize food waste by meal planning',
        'Choose organic foods when possible',
        'Grow your own herbs and vegetables',
        'Reduce packaging by buying in bulk'
    ],
    'consumption': [
        'Buy only what you need',
        'Choose quality items that last longer',
        'Repair instead of replacing when possible',
        'Buy second-hand or refurbished items',
        'Recycle and compost properly',
        'Reduce single-use plastics'
    ]
}

CARBON_FACTS = [
    'The average person produces about 4-5 tons of CO2 per year',
    'Transportation accounts for about 29% of greenhouse gas emissions',
    'Buildings are responsible for about 40% of energy consumption',
    'Food production contributes to about 26% of global emissions',
    'Recycling one ton of paper saves 3.3 cubic yards of landfill space'
]

@app.route('/services')
def services():
    user_id = session.get('user_id', 'demo_user')
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    return render_template('services.html', tips=CARBON_TIPS, facts=CARBON_FACTS, cart_count=len(cart), wishlist_count=len(wishlist))

@app.route('/calculator')
def calculator():
    user_id = session.get('user_id', 'demo_user')
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    return render_template('calculator.html', cart_count=len(cart), wishlist_count=len(wishlist))

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    transport_emissions = float(data.get('transport_miles', 0)) * 0.4  # kg CO2 per mile
    energy_emissions = float(data.get('energy_kwh', 0)) * 0.5  # kg CO2 per kWh
    diet_emissions = float(data.get('meat_meals', 0)) * 2.5  # kg CO2 per meat meal
    total_monthly = transport_emissions + energy_emissions + diet_emissions
    total_yearly = total_monthly * 12
    return jsonify({
        'monthly_emissions': round(total_monthly, 2),
        'yearly_emissions': round(total_yearly, 2),
        'comparison': get_comparison(total_yearly)
    })

def get_comparison(yearly_emissions):
    if yearly_emissions < 3000:
        return "Below average! You're doing great for the environment."
    elif yearly_emissions < 5000:
        return "Around average. There's room for improvement."
    else:
        return "Above average. Consider implementing more eco-friendly practices."

@app.route('/tips/<category>')
def category_tips(category):
    user_id = session.get('user_id', 'demo_user')
    cart = get_cart(user_id)
    wishlist = get_wishlist(user_id)
    if category in CARBON_TIPS:
        return render_template('tips.html', category=category, tips=CARBON_TIPS[category], cart_count=len(cart), wishlist_count=len(wishlist))
    return "Category not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
