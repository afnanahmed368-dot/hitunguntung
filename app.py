from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Indonesian Marketplace Fee Profiles (Simplified Tier Rates)
PLATFORM_FEES = {
    'shopee': {
        'name': 'Shopee',
        'regular': 0.04,        # 4.0%
        'star': 0.06,           # 6.0% Star / Star+ Seller
        'bebas_ongkir_extra': 0.04, # Free shipping program extra fee
    },
    'tokopedia': {
        'name': 'Tokopedia',
        'regular': 0.038,       # 3.8%
        'power_merchant': 0.055, # 5.5% Power Merchant
        'bebas_ongkir_extra': 0.03,
    },
    'tiktok': {
        'name': 'TikTok Shop',
        'regular': 0.045,       # 4.5%
        'star': 0.065,          # Creator / Brand partner tier
        'bebas_ongkir_extra': 0.035,
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    cost_price = float(data.get('cost_price', 0))
    sell_price = float(data.get('sell_price', 0))
    platform = data.get('platform', 'shopee')
    is_star = data.get('is_star', False)
    has_bebas_ongkir = data.get('has_bebas_ongkir', False)
    cod_risk_percent = float(data.get('cod_risk_percent', 0)) / 100

    plat_info = PLATFORM_FEES.get(platform, PLATFORM_FEES['shopee'])
    
    # Base admin fee rate
    base_rate = plat_info['star'] if is_star else plat_info['regular']
    
    # Extra voucher / free shipping fee rate
    extra_rate = plat_info['bebas_ongkir_extra'] if has_bebas_ongkir else 0.0
    
    total_fee_rate = base_rate + extra_rate
    admin_fee_amount = sell_price * total_fee_rate
    
    # COD return buffer estimate
    cod_loss_buffer = (cost_price * cod_risk_percent)
    
    total_cost = cost_price + admin_fee_amount + cod_loss_buffer
    net_profit = sell_price - total_cost
    margin_percentage = (net_profit / sell_price * 100) if sell_price > 0 else 0

    return jsonify({
        'sell_price': sell_price,
        'cost_price': cost_price,
        'admin_fee_amount': round(admin_fee_amount, 2),
        'admin_fee_rate_percent': round(total_fee_rate * 100, 2),
        'cod_loss_buffer': round(cod_loss_buffer, 2),
        'net_profit': round(net_profit, 2),
        'margin_percentage': round(margin_percentage, 2)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
