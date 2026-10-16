# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
import string
import time
import re

app = Flask(__name__)
CORS(app)


def generate_username(length=12):
    """Generate random username (lowercase letters and digits)."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def get_timestamp_id():
    """Return current timestamp in milliseconds."""
    return int(time.time() * 1000)


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def send_register_code_email(email):
    """
    Send registration code request to Garena.
    Returns: (result_dict, api_time)
    """
    url = "https://authgop.garena.com/api/send_register_code_email"

    headers = {
        "Host": "authgop.garena.com",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Linux",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://authgop.garena.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://authgop.garena.com/universal/register?redirect_uri=https://authgop.garena.com/universal/register",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en-IN;q=0.9,en;q=0.8,hi;q=0.7,vi;q=0.6",
        "Cookie": "_ga=GA1.1.868059803.1775926376; _ga_XB5PSHEQB4=GS2.1.s1775926375$o1$g1$t1775926378$j57$l0$h0; datadome=piPnlDyb63lxNPgE~RUOGoABXAAwgxiBV8pMUCVyDvaNK_SK5uvOTRikR~zsTIAAc5En_D133T364K7yxCfNS5YjVc3AKPIKU45GRmXGgJAoBnDU~rQ1xHE4esKMwfrh"
    }

    username = generate_username()
    request_id = get_timestamp_id()

    data = {
        "username": username,
        "email": email,
        "locale": "en-SG",
        "format": "json",
        "id": request_id
    }

    start = time.time()
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)  # ⚡ 30s → 10s (faster fail)
        api_time = round(time.time() - start, 3)
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text,
            "username": username,
            "request_id": request_id,
            "api_time": api_time
        }, api_time
    except Exception as e:
        api_time = round(time.time() - start, 3)
        return {
            "success": False,
            "error": str(e),
            "api_time": api_time
        }, api_time


# ══════════════════════════════════════════════════════════════
#   HOME
# ══════════════════════════════════════════════════════════════
@app.route('/', methods=['GET'])
def home():
    """Home endpoint."""
    return jsonify({
        "🎯 Credit": "KHAN",
        "📢 Join For More": "Telegram: @KHAN",
        "━━━━━━━━━━━━━━━━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "⚙️ Service": "Garena OTP API",
        "🔢 Version": "1.0",
        "✅ Status": "active",

        "━━━━━ 📡 ENDPOINTS ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "📮 POST /email_otp": "Send OTP with email in JSON body",
        "📮 GET /email_otp/<email>": "Send OTP with email in URL",
        "📮 GET /email_otp?email=xxx": "Send OTP with query parameter",

        "━━━━━ 💡 EXAMPLES ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "POST": "curl -X POST https://your-domain.vercel.app/email_otp -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\"}'",
        "GET URL": "curl https://your-domain.vercel.app/email_otp/user@example.com",
        "GET Query": "curl 'https://your-domain.vercel.app/email_otp?email=user@example.com'"
    })


# ══════════════════════════════════════════════════════════════
#   MAIN: /email_otp (POST + GET)
# ══════════════════════════════════════════════════════════════
@app.route('/email_otp', methods=['POST', 'GET'])
def send_otp():
    """Handle both POST and GET requests for OTP."""
    request_start = time.time()

    # ── Handle POST ─────────────────────────────
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "🎯 Credit": "KHAN",
                    "📢 Join For More": "Telegram: @KHAN",
                    "✅ STATUS": "❌ Error",
                    "🔢 Response Code": 400,
                    "❌ Error": "Invalid JSON body",
                    "⏱️ Total Time": f"{round(time.time() - request_start, 3)} sec"
                }), 400

            email = data.get('email')
        except Exception:
            return jsonify({
                "🎯 Credit": "KHAN",
                "📢 Join For More": "Telegram: @KHAN",
                "✅ STATUS": "❌ Error",
                "🔢 Response Code": 400,
                "❌ Error": "Invalid JSON format",
                "⏱️ Total Time": f"{round(time.time() - request_start, 3)} sec"
            }), 400
    else:
        email = request.args.get('email')

    # ── Validate email ──────────────────────────
    if not email:
        return jsonify({
            "🎯 Credit": "KHAN",
            "📢 Join For More": "Telegram: @KHAN",
            "✅ STATUS": "❌ Error",
            "🔢 Response Code": 400,
            "❌ Error": "Email is required. Use ?email=xxx for GET or JSON body for POST",
            "⏱️ Total Time": f"{round(time.time() - request_start, 3)} sec"
        }), 400

    if not validate_email(email):
        return jsonify({
            "🎯 Credit": "KHAN",
            "📢 Join For More": "Telegram: @KHAN",
            "✅ STATUS": "❌ Error",
            "🔢 Response Code": 400,
            "❌ Error": "Invalid email format",
            "⏱️ Total Time": f"{round(time.time() - request_start, 3)} sec"
        }), 400

    # ── Send OTP ────────────────────────────────
    result, api_time = send_register_code_email(email)
    total_time = round(time.time() - request_start, 3)

    # ── SUCCESS ─────────────────────────────────
    if result["success"]:
        return jsonify({
            "🎯 Credit": "KHAN",
            "📢 Join For More": "Telegram: @KHAN",
            "━━━━━━━━━━━━━━━━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "✅ STATUS": "✅ Success",
            "🔢 Response Code": 200,
            "💬 Message": "OTP sent successfully",

            "━━━━━ ⏱️ TIMING ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "⏳ Total Time": f"{total_time} sec",
            "🌐 API Time": f"{api_time} sec",

            "━━━━━ 📧 EMAIL INFO ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "📩 Email": email,
            "👤 Username": result.get("username"),
            "🆔 Request ID": result.get("request_id"),

            "━━━━━ 📡 SERVER ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "📨 Server Response": result.get("response")
        }), 200

    # ── ERROR ───────────────────────────────────
    return jsonify({
        "🎯 Credit": "KHAN",
        "📢 Join For More": "Telegram: @KHAN",
        "━━━━━━━━━━━━━━━━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "✅ STATUS": "❌ Failed",
        "🔢 Response Code": 500,
        "❌ Error": result.get("error", "Failed to send OTP"),
        "🔢 API Status": result.get("status_code"),

        "━━━━━ ⏱️ TIMING ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "⏳ Total Time": f"{total_time} sec",
        "🌐 API Time": f"{api_time} sec",

        "━━━━━ 📧 EMAIL INFO ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "📩 Email": email
    }), 500


# ══════════════════════════════════════════════════════════════
#   /email_otp/<email> (GET URL param)
# ══════════════════════════════════════════════════════════════
@app.route('/email_otp/<email>', methods=['GET'])
def send_otp_url(email):
    """Send OTP via GET request with email in URL."""
    request_start = time.time()

    if not email:
        return jsonify({
            "🎯 Credit": "KHAN",
            "📢 Join For More": "Telegram: @KHAN",
            "✅ STATUS": "❌ Error",
            "🔢 Response Code": 400,
            "❌ Error": "Email is required",
            "⏱️ Total Time": f"{round(time.time() - request_start, 3)} sec"
        }), 400

    if not validate_email(email):
        return jsonify({
            "🎯 Credit": "KHAN",
            "📢 Join For More": "Telegram: @KHAN",
            "✅ STATUS": "❌ Error",
            "🔢 Response Code": 400,
            "❌ Error": "Invalid email format",
            "⏱️ Total Time": f"{round(time.time() - request_start, 3)} sec"
        }), 400

    result, api_time = send_register_code_email(email)
    total_time = round(time.time() - request_start, 3)

    if result["success"]:
        return jsonify({
            "🎯 Credit": "KHAN",
            "📢 Join For More": "Telegram: @KHAN",
            "━━━━━━━━━━━━━━━━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "✅ STATUS": "✅ Success",
            "🔢 Response Code": 200,
            "💬 Message": "OTP sent successfully",

            "━━━━━ ⏱️ TIMING ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "⏳ Total Time": f"{total_time} sec",
            "🌐 API Time": f"{api_time} sec",

            "━━━━━ 📧 EMAIL INFO ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "📩 Email": email,
            "👤 Username": result.get("username"),
            "🆔 Request ID": result.get("request_id"),

            "━━━━━ 📡 SERVER ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
            "📨 Server Response": result.get("response")
        }), 200

    return jsonify({
        "🎯 Credit": "KHAN",
        "📢 Join For More": "Telegram: @KHAN",
        "━━━━━━━━━━━━━━━━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "✅ STATUS": "❌ Failed",
        "🔢 Response Code": 500,
        "❌ Error": result.get("error", "Failed to send OTP"),
        "🔢 API Status": result.get("status_code"),

        "━━━━━ ⏱️ TIMING ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "⏳ Total Time": f"{total_time} sec",
        "🌐 API Time": f"{api_time} sec",

        "━━━━━ 📧 EMAIL INFO ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "📩 Email": email
    }), 500


# ══════════════════════════════════════════════════════════════
#   ERROR HANDLERS
# ══════════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "🎯 Credit": "KHAN",
        "📢 Join For More": "Telegram: @KHAN",
        "✅ STATUS": "❌ Endpoint not found",
        "🔢 Response Code": 404,
        "━━━━━ 📡 AVAILABLE ━━━━━": "━━━━━━━━━━━━━━━━━━━━",
        "1": "/",
        "2": "/email_otp (POST with JSON body)",
        "3": "/email_otp?email=test@example.com (GET)",
        "4": "/email_otp/test@example.com (GET URL param)"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "🎯 Credit": "KHAN",
        "📢 Join For More": "Telegram: @KHAN",
        "✅ STATUS": "❌ Internal server error",
        "🔢 Response Code": 500
    }), 500


# Vercel requires this
app = app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)  # ⚡ debug=False for speed
