from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
import string
import time
import re
import os

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
    """Send registration code request to Garena."""
    url = "https://authgop.garena.com/api/send_register_code_email"
    
    # Headers exactly as in the provided request
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
    
    # Generate random username and id
    username = generate_username()
    request_id = get_timestamp_id()
    
    # Form data
    data = {
        "username": username,
        "email": email,
        "locale": "en-SG",
        "format": "json",
        "id": request_id
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text,
            "username": username,
            "request_id": request_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/', methods=['GET'])
def home():
    """Home endpoint."""
    return jsonify({
        "service": "Garena OTP API",
        "version": "1.0",
        "status": "active",
        "endpoints": {
            "/email_otp": "POST - Send OTP to email (body: email)",
            "/email_otp/<email>": "GET - Send OTP to email via URL parameter",
            "/email_otp?email=test@example.com": "GET - Send OTP via query parameter"
        },
        "example": {
            "post": "curl -X POST https://your-domain.vercel.app/email_otp -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\"}'",
            "get": "curl https://your-domain.vercel.app/email_otp/user@example.com"
        }
    })

@app.route('/email_otp', methods=['POST'])
def send_otp_post():
    """Send OTP via POST request with JSON body."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON body"
            }), 400
        
        email = data.get('email')
        
        if not email:
            return jsonify({
                "success": False,
                "error": "Email is required"
            }), 400
        
        if not validate_email(email):
            return jsonify({
                "success": False,
                "error": "Invalid email format"
            }), 400
        
        result = send_register_code_email(email)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "OTP sent successfully",
                "email": email,
                "username": result.get("username"),
                "request_id": result.get("request_id"),
                "response": result.get("response")
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to send OTP"),
                "status_code": result.get("status_code")
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/email_otp/<email>', methods=['GET'])
def send_otp_get(email):
    """Send OTP via GET request with email in URL."""
    if not email:
        return jsonify({
            "success": False,
            "error": "Email is required"
        }), 400
    
    if not validate_email(email):
        return jsonify({
            "success": False,
            "error": "Invalid email format"
        }), 400
    
    result = send_register_code_email(email)
    
    if result["success"]:
        return jsonify({
            "success": True,
            "message": "OTP sent successfully",
            "email": email,
            "username": result.get("username"),
            "request_id": result.get("request_id"),
            "response": result.get("response")
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": result.get("error", "Failed to send OTP"),
            "status_code": result.get("status_code")
        }), 500

@app.route('/email_otp', methods=['GET'])
def send_otp_get_param():
    """Send OTP via GET request with query parameter."""
    email = request.args.get('email')
    
    if not email:
        return jsonify({
            "success": False,
            "error": "Email parameter is required. Use ?email=example@domain.com"
        }), 400
    
    if not validate_email(email):
        return jsonify({
            "success": False,
            "error": "Invalid email format"
        }), 400
    
    result = send_register_code_email(email)
    
    if result["success"]:
        return jsonify({
            "success": True,
            "message": "OTP sent successfully",
            "email": email,
            "username": result.get("username"),
            "request_id": result.get("request_id"),
            "response": result.get("response")
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": result.get("error", "Failed to send OTP"),
            "status_code": result.get("status_code")
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# Vercel requires the app to be exported as 'app'
app = app

# For local development
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)