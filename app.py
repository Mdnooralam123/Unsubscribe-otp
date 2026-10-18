from flask import Flask, request, jsonify
import requests
import random
import string
import time
import re
import urllib3

# ✨ Chrome Impersonation for TLS fingerprint
try:
    from curl_cffi import requests as cffi_requests
    HAS_CFFI = True
except ImportError:
    HAS_CFFI = False

urllib3.disable_warnings()

app = Flask(__name__)
app.json.sort_keys = False


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
#   ✨ CORE FIX: Fresh Cookies + Chrome Impersonation
# ══════════════════════════════════════════════════════════════
def send_register_code_email(email):
    """
    Termux-friendly OTP sender.
    - Fresh session every request (no stale cookies)
    - Visits register page first to get valid Datadome cookie
    - Uses curl_cffi with Chrome impersonation (TLS fingerprint bypass)
    """
    username = generate_username()
    request_id = get_timestamp_id()
    
    data = {
        "username": username,
        "email": email,
        "locale": "en-SG",
        "format": "json",
        "id": request_id
    }
    
    USER_AGENT = "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    
    start = time.time()
    
    try:
        # ── Create session ────────────────────────
        if HAS_CFFI:
            session = cffi_requests.Session(impersonate="chrome124")
        else:
            session = requests.Session()
            session.verify = False
        
        # ═══ STEP 1: Visit register page (get fresh datadome cookie) ═══
        try:
            session.get(
                "https://authgop.garena.com/universal/register?redirect_uri=https://authgop.garena.com/universal/register",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
                    "User-Agent": USER_AGENT,
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Upgrade-Insecure-Requests": "1",
                },
                timeout=15,
                verify=False,
                allow_redirects=True
            )
        except Exception as e:
            app.logger.warning(f"[Pre-visit] {e}")
        
        # ═══ STEP 2: Also visit API host to set API-scoped cookies ═══
        try:
            session.get(
                "https://authgop.garena.com/universal/register",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "User-Agent": USER_AGENT,
                    "Referer": "https://authgop.garena.com/",
                },
                timeout=10,
                verify=False
            )
        except Exception:
            pass
        
        # ═══ STEP 3: Send OTP request ═══
        api_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://authgop.garena.com",
            "Referer": "https://authgop.garena.com/universal/register?redirect_uri=https://authgop.garena.com/universal/register",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": USER_AGENT,
            "X-Requested-With": "XMLHttpRequest",
        }
        
        response = session.post(
            "https://authgop.garena.com/api/send_register_code_email",
            headers=api_headers,
            data=data,
            timeout=20,
            verify=False
        )
        
        api_time = round(time.time() - start, 3)
        
        # ═══ STEP 4: Parse response ═══
        is_success = response.status_code == 200
        resp_text = response.text[:500]
        resp_json = None
        
        try:
            resp_json = response.json()
            code_val = resp_json.get("code")
            if code_val is not None and code_val != 0:
                is_success = False
            if resp_json.get("error"):
                is_success = False
        except Exception:
            pass
        
        # Check for captcha in response (DataDome block)
        if "captcha-delivery" in resp_text or "geo.captcha-delivery" in resp_text:
            is_success = False
        
        # ═══ Success response ═══
        if is_success and resp_json:
            return {
                "success": True,
                "status_code": response.status_code,
                "response": resp_text,
                "username": username,
                "request_id": request_id,
                "api_time": api_time,
                "method": "curl_cffi (chrome124)" if HAS_CFFI else "requests"
            }, api_time
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "response": resp_text,
                "username": username,
                "request_id": request_id,
                "api_time": api_time,
                "method": "curl_cffi (chrome124)" if HAS_CFFI else "requests",
                "error": f"HTTP {response.status_code} — DataDome/Captcha block"
            }, api_time
    
    except Exception as e:
        api_time = round(time.time() - start, 3)
        return {
            "success": False,
            "error": str(e),
            "api_time": api_time,
            "method": "curl_cffi (chrome124)" if HAS_CFFI else "requests"
        }, api_time


# ══════════════════════════════════════════════════════════════
#   HOME
# ══════════════════════════════════════════════════════════════
@app.route('/', methods=['GET'])
def home():
    return jsonify(build_response(
        "🟢 Online", 200,
        data={
            "⚙️ SERVICE INFO": {
                "🤖 Service": "Garena OTP API (Termux Fixed)",
                "🔢 Version": "3.0",
                "🚀 Method": "curl_cffi + Fresh Cookies" if HAS_CFFI else "requests (fallback)"
            },
            "📡 ENDPOINTS": {
                "📮 POST /email_otp": "Send OTP (JSON body)",
                "📮 GET /email_otp/<email>": "Send OTP (URL param)",
                "📮 GET /email_otp?email=xxx": "Send OTP (query param)"
            }
        }
    ))


# ══════════════════════════════════════════════════════════════
#   OTP HANDLERS
# ══════════════════════════════════════════════════════════════
@app.route('/email_otp', methods=['POST', 'GET'])
def send_otp():
    start_time = time.time()
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify(build_response("❌ Error", 400, error="Invalid JSON body", total_time=time.time() - start_time)), 400
            email = data.get('email')
        except Exception:
            return jsonify(build_response("❌ Error", 400, error="Invalid JSON format", total_time=time.time() - start_time)), 400
    else:
        email = request.args.get('email')

    if not email:
        return jsonify(build_response("❌ Error", 400, error="Email is required", total_time=time.time() - start_time)), 400

    if not validate_email(email):
        return jsonify(build_response("❌ Error", 400, error="Invalid email format", total_time=time.time() - start_time)), 400

    result, api_time = send_register_code_email(email)
    total_time = round(time.time() - start_time, 3)
    
    sections = {
        "📧 EMAIL INFO": {
            "📩 Email": email,
            "👤 Username": result.get("username"),
            "🆔 Request ID": result.get("request_id"),
        },
        "🌐 API INFO": {
            "📡 API Status": result.get("status_code"),
            "🚀 Method": result.get("method"),
            "📨 Server Response": (result.get("response") or "")[:200]
        }
    }
    
    if result.get("success"):
        return jsonify(build_response("✅ OTP Sent", 200, data=sections, total_time=total_time, api_time=api_time)), 200
    else:
        return jsonify(build_response(
            "❌ Failed", 500, data=sections,
            error=result.get("error", "Failed to send OTP"),
            total_time=total_time, api_time=api_time
        )), 500


@app.route('/email_otp/<email>', methods=['GET'])
def send_otp_url(email):
    start_time = time.time()
    
    if not email or not validate_email(email):
        return jsonify(build_response("❌ Error", 400, error="Invalid email", total_time=time.time() - start_time)), 400

    result, api_time = send_register_code_email(email)
    total_time = round(time.time() - start_time, 3)
    
    sections = {
        "📧 EMAIL INFO": {
            "📩 Email": email,
            "👤 Username": result.get("username"),
            "🆔 Request ID": result.get("request_id"),
        },
        "🌐 API INFO": {
            "📡 API Status": result.get("status_code"),
            "🚀 Method": result.get("method"),
        }
    }
    
    if result.get("success"):
        return jsonify(build_response("✅ OTP Sent", 200, data=sections, total_time=total_time, api_time=api_time)), 200
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
    return jsonify(build_response("❌ Endpoint Not Found", 404, error="Check / for available endpoints")), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify(build_response("❌ Internal Server Error", 500)), 500


# Vercel requires this
app = app


if __name__ == "__main__":
    print("=" * 55)
    print("🔥 Garena OTP API — Termux Fixed")
    print("=" * 55)
    print(f"🚀 Method: {'curl_cffi (chrome124)' if HAS_CFFI else 'requests (fallback)'}")
    print("🌐 Server: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(host='0.0.0.0', port=5000, debug=False)
