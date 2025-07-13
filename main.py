
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import hashlib
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = 'ecomart_carbonnft_secret_key'

# Mock database for demonstration
users_db = {}
purchases_db = []
nft_badges_db = {}

# NFT Badge tiers and requirements
NFT_TIERS = {
    'green_starter': {'name': 'Green Starter', 'co2_required': 5, 'color': '#28a745'},
    'eco_warrior': {'name': 'Eco Warrior', 'co2_required': 20, 'color': '#fd7e14'},
    'planet_protector': {'name': 'Planet Protector', 'co2_required': 50, 'color': '#6c757d'},
    'climate_champion': {'name': 'Climate Champion', 'co2_required': 100, 'color': '#6f42c1'}
}

# Sample eco-products
ECO_PRODUCTS = [
    {'id': 1, 'name': 'Organic Cotton T-Shirt', 'price': 25.99, 'co2_saved': 2.3, 'category': 'clothing'},
    {'id': 2, 'name': 'LED Light Bulbs (4-pack)', 'price': 12.99, 'co2_saved': 8.7, 'category': 'electronics'},
    {'id': 3, 'name': 'Recycled Paper Towels', 'price': 8.49, 'co2_saved': 1.2, 'category': 'household'},
    {'id': 4, 'name': 'Solar Phone Charger', 'price': 49.99, 'co2_saved': 15.4, 'category': 'electronics'},
    {'id': 5, 'name': 'Bamboo Toothbrush Set', 'price': 14.99, 'co2_saved': 3.1, 'category': 'personal_care'},
    {'id': 6, 'name': 'Reusable Water Bottle', 'price': 19.99, 'co2_saved': 5.8, 'category': 'lifestyle'}
]

def get_user_data(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            'total_co2_saved': 0,
            'monthly_co2_saved': 0,
            'eco_products_purchased': 0,
            'monthly_goal': 25,
            'eco_products_goal': 15,
            'last_reset': datetime.now().replace(day=1),
            'nft_badges': []
        }
    return users_db[user_id]

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
            # Award NFT badge
            nft_id = str(uuid.uuid4())
            badge_data = {
                'id': nft_id,
                'tier': tier_id,
                'name': tier_info['name'],
                'co2_saved': total_co2,
                'earned_date': datetime.now().isoformat(),
                'metadata': {
                    'description': f'NFT Badge for saving {tier_info["co2_required"]}+ kg CO2',
                    'image_url': f'/static/badges/{tier_id}.png',
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
    
    return render_template('index.html', user_data=user_data, eco_products=ECO_PRODUCTS)

@app.route('/rewards')
def rewards():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    check_monthly_reset(user_data)
    
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
                         user_nft_badges=user_nft_badges)

@app.route('/purchase', methods=['POST'])
def purchase():
    user_id = session.get('user_id', 'demo_user')
    product_id = int(request.json.get('product_id'))
    
    # Find product
    product = next((p for p in ECO_PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    user_data = get_user_data(user_id)
    check_monthly_reset(user_data)
    
    # Update user stats
    user_data['total_co2_saved'] += product['co2_saved']
    user_data['monthly_co2_saved'] += product['co2_saved']
    user_data['eco_products_purchased'] += 1
    
    # Record purchase
    purchase_record = {
        'id': len(purchases_db) + 1,
        'user_id': user_id,
        'product': product,
        'timestamp': datetime.now().isoformat(),
        'co2_saved': product['co2_saved']
    }
    purchases_db.append(purchase_record)
    
    # Check for new NFT badges
    new_badges = check_and_award_nft_badges(user_id, user_data)
    
    return jsonify({
        'success': True,
        'co2_saved': product['co2_saved'],
        'total_co2_saved': user_data['total_co2_saved'],
        'new_badges': new_badges
    })

@app.route('/mint_nft', methods=['POST'])
def mint_nft():
    user_id = session.get('user_id', 'demo_user')
    badge_id = request.json.get('badge_id')
    
    if badge_id not in nft_badges_db:
        return jsonify({'success': False, 'message': 'Badge not found'})
    
    badge_data = nft_badges_db[badge_id]
    
    # Simulate NFT minting process
    mint_hash = hashlib.sha256(f"{badge_id}{user_id}{datetime.now().isoformat()}".encode()).hexdigest()
    
    badge_data['minted'] = True
    badge_data['mint_hash'] = mint_hash
    badge_data['mint_date'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'mint_hash': mint_hash,
        'badge': badge_data
    })

@app.route('/api/user_stats')
def user_stats():
    user_id = session.get('user_id', 'demo_user')
    user_data = get_user_data(user_id)
    check_monthly_reset(user_data)
    
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
