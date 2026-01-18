


from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG_FILE = 'config.json'
ADMIN_PASSWORD = 'tasba'
YOUR_EMAIL = 'tahahashmi314@gmail.com'
YOUR_APP_PASSWORD = 'styu uree fdme cccc'  # You'll set this up

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Store sent notifications
sent_notifications = set()

# Load/Save Config
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'target_datetime': '2025-12-24T13:00:00',
        'victim_email': '',
        'scheduler_running': False
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Email sending function
def send_email(subject, body, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = YOUR_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        # Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent: {subject} to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# Email templates
def get_email_template(minutes_remaining):
    if minutes_remaining == 30:
        return {
            'subject': '⚠️ 30 MINUTES WARNING - THE SLAP APPROACHES',
            'body': f'''
            <html>
            <body style="background: linear-gradient(135deg, #000 0%, #1a0000 100%); padding: 40px; font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 15px; padding: 40px; border: 5px solid #ff0000;">
                    <h1 style="color: #ff0000; text-align: center; font-size: 36px;">⚠️ WARNING ⚠️</h1>
                    <h2 style="text-align: center; color: #333;">Only 30 Minutes Remaining</h2>
                    <p style="font-size: 18px; text-align: center; color: #666;">
                        Dear Samsheer,<br><br>
                        The moment you've been dreading is almost here.<br>
                        <strong style="color: #ff0000;">SLAP #5</strong> will be delivered in exactly <strong>30 minutes</strong>.
                    </p>
                    <div style="background: #ffebee; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #ff0000; text-align: center;">👋 SLAP BET STATUS 👋</h3>
                        <p style="text-align: center; font-size: 24px;">4 SLAPS DELIVERED • 1 REMAINING</p>
                    </div>
                    <p style="text-align: center; color: #999; font-style: italic;">
                        "The final slap is not just a slap... it's destiny."
                    </p>
                </div>
            </body>
            </html>
            '''
        }
    elif minutes_remaining == 15:
        return {
            'subject': '🚨 15 MINUTES - PREPARE YOURSELF',
            'body': '''
            <html>
            <body style="background: #000; padding: 40px; font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; background: #1a0000; border-radius: 15px; padding: 40px; border: 5px solid #ff0000;">
                    <h1 style="color: #ff0000; text-align: center; font-size: 42px; animation: pulse 1s infinite;">🚨 15 MINUTES 🚨</h1>
                    <p style="font-size: 20px; text-align: center; color: #fff;">
                        The countdown continues...<br><br>
                        <strong style="color: #ff0000; font-size: 28px;">15 MINUTES</strong> until impact.
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="font-size: 60px;">👋</div>
                        <p style="color: #ff0000; font-size: 24px; margin-top: 10px;">THE HAND OF JUSTICE</p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
    elif minutes_remaining == 10:
        return {
            'subject': '⏰ 10 MINUTES - THE FINAL COUNTDOWN',
            'body': '''
            <html>
            <body style="background: #000; padding: 40px; font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; background: #1a0000; border-radius: 15px; padding: 40px; border: 5px solid #ff0000;">
                    <h1 style="color: #ff0000; text-align: center; font-size: 48px;">⏰ 10 MINUTES ⏰</h1>
                    <p style="font-size: 22px; text-align: center; color: #fff;">
                        Single digits, Samsheer.<br>
                        <strong style="color: #ff0000;">TEN. MINUTES.</strong>
                    </p>
                    <div style="background: #ff0000; color: #fff; padding: 20px; text-align: center; border-radius: 10px; margin: 20px 0;">
                        <h2>YOUR FATE IS SEALED</h2>
                        <p style="font-size: 18px;">There is no escape. Accept your destiny.</p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
    elif minutes_remaining == 5:
        return {
            'subject': '🔥 5 MINUTES - BRACE YOURSELF 🔥',
            'body': '''
            <html>
            <body style="background: #000; padding: 40px; font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; background: #1a0000; border-radius: 15px; padding: 40px; border: 5px solid #ff0000; box-shadow: 0 0 50px #ff0000;">
                    <h1 style="color: #ff0000; text-align: center; font-size: 56px; text-shadow: 0 0 20px #ff0000;">🔥 5 MINUTES 🔥</h1>
                    <p style="font-size: 24px; text-align: center; color: #fff; line-height: 1.6;">
                        This is it.<br>
                        <strong style="color: #ff0000; font-size: 32px;">FIVE MINUTES</strong><br>
                        until the legendary 5th slap.
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="font-size: 80px;">👋💥</div>
                    </div>
                    <p style="text-align: center; color: #ff6666; font-size: 20px;">
                        PREPARE YOUR FACE
                    </p>
                </div>
            </body>
            </html>
            '''
        }
    else:  # 0 minutes - SLAP TIME
        return {
            'subject': '💥💥💥 SLAP TIME! RIGHT NOW! 💥💥💥',
            'body': '''
            <html>
            <body style="background: #ff0000; padding: 40px; font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; background: #000; border-radius: 15px; padding: 40px; border: 10px solid #ff0000; box-shadow: 0 0 100px #ff0000;">
                    <h1 style="color: #ff0000; text-align: center; font-size: 64px; animation: pulse 0.5s infinite;">💥 SLAP TIME! 💥</h1>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="font-size: 120px;">👋</div>
                    </div>
                    <p style="font-size: 28px; text-align: center; color: #fff; font-weight: bold;">
                        TIME'S UP, SAMSHEER!<br><br>
                        <span style="color: #ff0000; font-size: 36px;">THE 5TH SLAP IS HERE!</span>
                    </p>
                    <div style="background: #ff0000; color: #000; padding: 30px; text-align: center; border-radius: 10px; margin: 30px 0; font-size: 24px; font-weight: bold;">
                        SLAP BET COMPLETED: 5/5 ✓
                    </div>
                    <p style="text-align: center; color: #999; font-size: 18px; font-style: italic;">
                        "And that's how it's done." - The Slap Master
                    </p>
                </div>
            </body>
            </html>
            '''
        }

# Check and send notifications
def check_and_send_notifications():
    config = load_config()
    
    if not config.get('scheduler_running', False):
        return
    
    victim_email = config.get('victim_email', '')
    if not victim_email:
        return
    
    target_dt = datetime.fromisoformat(config['target_datetime'])
    target_dt = IST.localize(target_dt)
    now = datetime.now(IST)
    
    time_diff = (target_dt - now).total_seconds() / 60  # minutes
    
    # Check for each notification time
    for minutes in [30, 15, 10, 5, 0]:
        notification_key = f'{minutes}min'
        
        # If we're within 1 minute of the notification time and haven't sent it yet
        if abs(time_diff - minutes) < 1 and notification_key not in sent_notifications:
            email_data = get_email_template(minutes)
            success = send_email(email_data['subject'], email_data['body'], victim_email)
            
            if success:
                sent_notifications.add(notification_key)
                print(f"✅ Sent {minutes} minute notification")

# API Routes
@app.route('/')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/countdown')
def countdown():
    return send_from_directory('.', 'countdown.html')

@app.route('/api/config', methods=['GET', 'POST'])
def config_api():
    if request.method == 'POST':
        data = request.json
        config = load_config()
        config.update(data)
        save_config(config)
        return jsonify({'success': True, 'config': config})
    else:
        return jsonify(load_config())

@app.route('/api/start-scheduler', methods=['POST'])
def start_scheduler():
    config = load_config()
    config['scheduler_running'] = True
    save_config(config)
    
    # Schedule the check function to run every minute
    if not scheduler.get_job('notification_checker'):
        scheduler.add_job(
            check_and_send_notifications,
            'interval',
            minutes=1,
            id='notification_checker'
        )
    
    return jsonify({'success': True, 'message': 'Scheduler started'})

@app.route('/api/stop-scheduler', methods=['POST'])
def stop_scheduler():
    config = load_config()
    config['scheduler_running'] = False
    save_config(config)
    
    if scheduler.get_job('notification_checker'):
        scheduler.remove_job('notification_checker')
    
    return jsonify({'success': True, 'message': 'Scheduler stopped'})

@app.route('/api/test-email', methods=['POST'])
def test_email_api():
    config = load_config()
    victim_email = config.get('victim_email', '')
    
    if not victim_email:
        return jsonify({'success': False, 'message': 'No email configured'})
    
    subject = '🧪 TEST - Slap Countdown System'
    body = '''
    <html>
    <body style="padding: 40px; font-family: Arial, sans-serif;">
        <h2>Test Email - Slap Countdown System</h2>
        <p>This is a test email. The system is working!</p>
        <p>You will receive notifications at: 30min, 15min, 10min, 5min, and 0min before the slap.</p>
    </body>
    </html>
    '''
    
    success = send_email(subject, body, victim_email)
    
    return jsonify({
        'success': success,
        'message': 'Test email sent!' if success else 'Failed to send email'
    })

@app.route('/api/status', methods=['GET'])
def status():
    config = load_config()
    target_dt = datetime.fromisoformat(config['target_datetime'])
    target_dt = IST.localize(target_dt)
    now = datetime.now(IST)
    
    time_remaining = target_dt - now
    
    return jsonify({
        'scheduler_running': config.get('scheduler_running', False),
        'time_remaining_seconds': int(time_remaining.total_seconds()),
        'sent_notifications': list(sent_notifications),
        'victim_email': config.get('victim_email', 'Not set')
    })

if __name__ == '__main__':
    print("🚀 Slap Countdown Backend Starting...")
    print(f"📧 Email: {YOUR_EMAIL}")
    print(f"⏰ Target: December 24, 2025, 1:00 PM IST")
    print(f"🔐 Admin Password: {ADMIN_PASSWORD}")
    print("\n⚠️ IMPORTANT: Set YOUR_APP_PASSWORD before running!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)