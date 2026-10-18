from flask import Flask, request, jsonify
import requests
import random
import string
import time
import re
from collections import OrderedDict

# ✨ Best bypass for Datadome (TLS fingerprint impersonation)
try:
    from curl_cffi import requests as cffi_requests
    USE_CURL_CFFI = True
except ImportError:
    USE_CURL_CFFI = False

app = Flask(__name__)
app.json.sort_keys = False  # ✨ Order preserve karne ke liye

# ══════════════════════════════════════════════════════════════
#   HELPERS
# ══════════════════════════════════════════════════════════════
def generate_username(length=12):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def get_timestamp_id():
    return int(time.time() * 1000)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ✨ PREMIUM RESPONSE BUILDER
def build_response(title, code, data=None, error=None, total_time=None, api_time=None):
    resp = {
        "🎯 Credit": "KHAN",
        "📢 Join For More": "Telegram: @KHAN",
        "═══════════════════════════════════": "═══════════════════════════════════",
        "✅ STATUS": title,
        "🔢 Response Code": code,
    }
    
    if error:
        resp["❌ Error"] = error

    if total_time is not None:
        resp["─────────── ⏱️ TIMING ───────────"] = "───────────────────────────────────"
        resp["⏳ Total Time"] = f"{round(total_time, 3)} sec"
        resp["🌐 API Time"] = f"{round(api_time or 0, 3)} sec"

    if data:
        for section_name, section_data in data.items():
            resp[f"─────────── {section_name} ───────────"] = "───────────────────────────────────"
            resp.update(section_data)
            
    return resp

# ══════════════════════════════════════════════════════════════
#   ✨ MAIN OTP SENDER (FIXED for 403)
# ══════════════════════════════════════════════════════════════
def send_register_code_email(email):
    url = "https://authgop.garena.com/api/send_register_code_email"
    
    username = generate_username()
    request_id = get_timestamp_id()
    
    data = {
        "username": username,
        "email": email,
        "locale": "en-SG",
        "format": "json",
        "id": request_id
    }
    
    # Browser headers (no stale datadome cookie!)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://authgop.garena.com",
        "Referer": "https://authgop.garena.com/universal/register?redirect_uri=https://authgop.garena.com/universal/register",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    
    start = time.time()
    
    try:
        # ✨ Create FRESH session each time (curl_cffi if available)
        if USE_CURL_CFFI:
            session = cffi_requests.Session(impersonate="chrome120")
        else:
            session = requests.Session()
            session.verify = False
            # Suppress warnings
            import urllib3
            urllib3.disable_warnings()
        
        # ═══ STEP 1: Visit register page to get fresh cookies ═══
        try:
            session.get(
                "https://authgop.garena.com/universal/register?redirect_uri=https://authgop.garena.com/universal/register",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "User-Agent": headers["User-Agent"],
                },
                timeout=15,
                verify=False
            )
        except Exception as e:
            app.logger.warning(f"Pre-visit failed (continuing anyway): {e}")
        
        # ═══ STEP 2: Send OTP request with fresh cookies ═══
        response = session.post(url, headers=headers, data=data, timeout=20, verify=False)
        api_time = round(time.time() - start, 3)
        
        # ═══ STEP 3: Parse and verify response ═══
        is_success = response.status_code == 200
        resp_text = response.text
        resp_json = None
        
        try:
            resp_json = response.json()
        except:
            pass
        
        # Check if Garena returned error in body (even with 200 status)
        if is_success and isinstance(resp_json, dict):
            # Common error indicators
            code_val = resp_json.get("code")
            if code_val is not None and code_val != 0:
                is_success = False
            if resp_json.get("error"):
                is_success = False
            if resp_json.get("error_code"):
                is_success = False
        
        # Cookie header update (for debugging)
        new_cookies = "; ".join([f"{k}={v}" for k, v in session.cookies.items()])
        
        return {
            "success": is_success,
            "status_code": response.status_code,
            "response": resp_text[:500],  # truncate for response
            "username": username,
            "request_id": request_id,
            "api_time": api_time,
            "used_curl_cffi": USE_CURL_CFFI
        }, api_time
        
    except Exception as e:
        api_time = round(time.time() - start, 3)
        return {
            "success": False,
            "error": str(e),
            "status_code": None,
            "api_time": api_time
        }, api_time

# ══════════════════════════════════════════════════════════════
#   HOME
# ══════════════════════════════════════════════════════════════
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        **build_response("🟢 Online", 200, {
            "⚙️ SERVICE INFO": {
                "Service": "Garena OTP API",
                "Version": "2.0",
                "Datadome Bypass": "curl_cffi" if USE_CURL_CFFI else "requests (fallback)"
            },
            "📡 ENDPOINTS": {
                "📮 POST /email_otp": "Send OTP (JSON body)",
                "📮 GET /email_otp/<email>": "Send OTP (URL param)",
                "📮 GET /email_otp?email=xxx": "Send OTP (query)",
            },
            "💡 EXAMPLES": {
                "POST": "curl -X POST https://your-domain/api/email_otp -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\"}'",
                "GET URL": "curl https://your-domain/api/email_otp/user@example.com",
                "GET Query": "curl 'https://your-domain/api/email_otp?email=user@example.com'",
            }
        })
    })

# ══════════════════════════════════════════════════════════════
#   MAIN OTP HANDLER
# ══════════════════════════════════════════════════════════════
@app.route('/email_otp', methods=['POST', 'GET'])
def send_otp():
    start_time = time.time()
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify(build_response(
                    "❌ Error", 400, error="Invalid JSON body",
                    total_time=time.time() - start_time
                )), 400
            email = data.get('email')
        except Exception:
            return jsonify(build_response(
                "❌ Error", 400, error="Invalid JSON format",
                total_time=time.time() - start_time
            )), 400
    else:
        email = request.args.get('email')

    if not email:
        return jsonify(build_response(
            "❌ Error", 400, error="Email is required",
            total_time=time.time() - start_time
        )), 400

    if not validate_email(email):
        return jsonify(build_response(
            "❌ Error", 400, error="Invalid email format",
            total_time=time.time() - start_time
        )), 400

    result, api_time = send_register_code_email(email)
    total_time = time.time() - start_time
    
    sections = {
        "📧 EMAIL INFO": {
            "📩 Email": email,
            "👤 Username": result.get("username"),
            "🆔 Request ID": result.get("request_id"),
        },
        "🌐 API INFO": {
            "📡 API Status": result.get("status_code"),
            "🚀 Method": "curl_cffi" if result.get("used_curl_cffi") else "requests",
            "📨 Server Response": (result.get("response") or "")[:200]
        }
    }
    
    if result.get("success"):
        return jsonify(build_response(
            "✅ OTP Sent", 200, data=sections,
            total_time=total_time, api_time=api_time
        )), 200
    else:
        return jsonify(build_response(
            "❌ Failed", 500, data=sections,
            error=result.get("error", "Failed to send OTP (Datadome block or API error)"),
            total_time=total_time, api_time=api_time
        )), 500

# ══════════════════════════════════════════════════════════════
#   URL PARAM HANDLER
# ══════════════════════════════════════════════════════════════
@app.route('/email_otp/<email>', methods=['GET'])
def send_otp_url(email):
    start_time = time.time()
    
    if not email or not validate_email(email):
        return jsonify(build_response(
            "❌ Error", 400, error="Invalid or missing email",
            total_time=time.time() - start_time
        )), 400

    result, api_time = send_register_code_email(email)
    total_time = time.time() - start_time
    
    sections = {
        "📧 EMAIL INFO": {
            "📩 Email": email,
            "👤 Username": result.get("username"),
            "🆔 Request ID": result.get("request_id"),
        },
        "🌐 API INFO": {
            "📡 API Status": result.get("status_code"),
            "🚀 Method": "curl_cffi" if result.get("used_curl_cffi") else "requests",
        }
    }
    
    if result.get("success"):
        return jsonify(build_response(
            "✅ OTP Sent", 200, data=sections,
            total_time=total_time, api_time=api_time
        )), 200
    else:
        return jsonify(build_response(
            "❌ Failed", 500, data=sections,
            error=result.get("error", "Failed to send OTP"),
            total_time=total_time, api_time=api_time
        )), 500

# ══════════════════════════════════════════════════════════════
#   ERROR HANDLERS
# ══════════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(error):
    return jsonify(build_response(
        "❌ Endpoint Not Found", 404,
        error="Check available endpoints at /"
    )), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(build_response(
        "❌ Internal Server Error", 500
    )), 500

# Vercel requires this
app = app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
