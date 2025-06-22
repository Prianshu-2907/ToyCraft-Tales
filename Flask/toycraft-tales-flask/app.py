from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import socket
import subprocess
import threading
import time
import requests
import os
import sys
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import db_manager

app = Flask(__name__)
app.secret_key = 'ToyCraft2024!DataViz#Analytics$SecureKey789'

# Email Configuration (Update these with your email settings)
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',  # For Gmail
    'SMTP_PORT': 587,
    'EMAIL': 'prince56jyo@gmail.com',  # Your email
    'PASSWORD': 'lwmu pjqz exsk orof',   # Your email app password
    'FROM_NAME': 'ToyCraft Tales'
}

class NgrokManager:
    def __init__(self):
        self.tunnel_url = None
        self.tunnel_process = None
        self.ngrok_started = False
    
    def start_ngrok(self, port=5000):
        """Start ngrok tunnel"""
        try:
            print("🚀 Starting ngrok tunnel...")
            
            self.tunnel_process = subprocess.Popen(
                ['ngrok', 'http', str(port), '--log=stdout'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(4)
            
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                if response.status_code == 200:
                    tunnels_data = response.json()
                    if tunnels_data.get('tunnels'):
                        for tunnel in tunnels_data['tunnels']:
                            if tunnel['proto'] == 'https':
                                self.tunnel_url = tunnel['public_url']
                                self.ngrok_started = True
                                return self.tunnel_url
                        
                        self.tunnel_url = tunnels_data['tunnels'][0]['public_url']
                        self.ngrok_started = True
                        return self.tunnel_url
                        
            except requests.exceptions.RequestException as e:
                print(f"❌ Error connecting to ngrok API: {e}")
                
        except FileNotFoundError:
            print("❌ ngrok not found! Please install ngrok first")
            return None
        except Exception as e:
            print(f"❌ Failed to start ngrok: {e}")
            return None
    
    def stop_tunnel(self):
        """Stop the ngrok tunnel"""
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
                print("🛑 Ngrok tunnel stopped")
            except:
                self.tunnel_process.kill()

def get_local_ip():
    """Get the local IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def test_database_connection():
    """Test database connection and display status"""
    try:
        count = db_manager.get_contact_count()
        print(f"✅ Database connected successfully! Current contacts: {count}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def validate_email(email):
    """Validate email format"""
    if not email or '@' not in email:
        return False, "Invalid email format"
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, "Valid email"

def validate_phone(phone):
    """Validate 10-digit phone number"""
    if not phone:
        return False, "Phone number is required"
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    if len(digits_only) != 10:
        return False, "Phone number must be exactly 10 digits"
    
    # Check if it starts with valid digits (not 0 or 1)
    if digits_only[0] in ['0', '1']:
        return False, "Phone number cannot start with 0 or 1"
    
    return True, "Valid phone number"

def send_welcome_email(name, email):
    """Send welcome email to new contact"""
    try:
        if not all([EMAIL_CONFIG['EMAIL'], EMAIL_CONFIG['PASSWORD']]):
            print("⚠️ Email configuration not set up")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['FROM_NAME']} <{EMAIL_CONFIG['EMAIL']}>"
        msg['To'] = email
        msg['Subject'] = "🎉 Welcome to ToyCraft Tales Community!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea; margin-bottom: 10px;">🎯 Welcome to ToyCraft Tales!</h1>
                    <p style="font-size: 18px; color: #666;">Hi {name}! 👋</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 30px; border-radius: 15px; margin-bottom: 20px;">
                    <h2 style="color: #2d3748; margin-bottom: 15px;">✨ Thank you for joining us!</h2>
                    <p style="margin-bottom: 15px;">We're excited to have you as part of our ToyCraft Tales community. You'll now receive updates about:</p>
                    <ul style="margin-bottom: 20px;">
                        <li>🎨 Latest toy craft ideas and tutorials</li>
                        <li>📊 Interactive data visualizations and insights</li>
                        <li>🎪 Fun stories and creative content</li>
                        <li>🎁 Exclusive community benefits</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 16px; color: #666;">
                        Stay tuned for amazing content and updates!<br>
                        <strong>The ToyCraft Tales Team</strong> 🚀
                    </p>
                </div>
                
                <div style="text-align: center; padding: 20px; background: #f8fafc; border-radius: 10px; margin-top: 20px;">
                    <p style="font-size: 14px; color: #999; margin: 0;">
                        This email was sent to {email}<br>
                        © 2025 ToyCraft Tales. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        server.starttls()
        server.login(EMAIL_CONFIG['EMAIL'], EMAIL_CONFIG['PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        print(f"📧 Welcome email sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
        return False

# Initialize ngrok manager
ngrok = NgrokManager()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission with enhanced validation"""
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        
        # Validate all fields are present
        if not name or not email or not phone:
            flash('All fields are required!', 'error')
            return redirect(url_for('index'))
        
        # Validate name
        if len(name) < 2:
            flash('Name must be at least 2 characters long!', 'error')
            return redirect(url_for('index'))
        
        if len(name) > 50:
            flash('Name cannot exceed 50 characters!', 'error')
            return redirect(url_for('index'))
        
        # Validate email format
        email_valid, email_message = validate_email(email)
        if not email_valid:
            flash(f'Email validation failed: {email_message}', 'error')
            return redirect(url_for('index'))
        
        # Validate phone
        phone_valid, phone_message = validate_phone(phone)
        if not phone_valid:
            flash(f'Phone validation failed: {phone_message}', 'error')
            return redirect(url_for('index'))
        
        # Clean phone number (keep only digits)
        phone_clean = re.sub(r'\D', '', phone)
        
        # Check if email already exists - FIXED VERSION
        try:
            existing_contacts = db_manager.get_all_contacts()
            for contact in existing_contacts:
                # Now contact is a Contact object, so we can use .email
                if contact.email and contact.email.lower() == email.lower():
                    flash(f'Welcome back {name}! This email is already registered with us.', 'success')
                    return redirect(url_for('index'))
        except Exception as e:
            print(f"⚠️ Warning: Could not check for existing contacts: {e}")
            # Continue with registration even if we can't check for duplicates
        
        # Get additional info
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # Add contact to database
        success = db_manager.add_contact(
            name=name,
            email=email,
            phone=phone_clean,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if success:
            # Send welcome email
            email_sent = send_welcome_email(name, email)
            
            if email_sent:
                flash(f'🎉 Welcome {name}! Your details have been submitted successfully and a welcome email has been sent to {email}.', 'success')
            else:
                flash(f'✅ Thank you {name}! Your details have been submitted successfully.', 'success')
            
            print(f"📝 New contact added: {name} ({email}) - Phone: {phone_clean}")
        else:
            flash('Sorry, there was a database error. Please try again.', 'error')
            
    except Exception as e:
        print(f"❌ Error in submit_contact: {e}")
        flash('An unexpected error occurred. Please try again later.', 'error')
    
    return redirect(url_for('index'))

@app.route('/contacts')
def view_contacts():
    """View all contacts (admin page)"""
    try:
        contacts = db_manager.get_all_contacts()
        return render_template('admin_contacts.html', contacts=contacts)
    except Exception as e:
        print(f"❌ Error fetching contacts: {e}")
        flash('Error loading contacts', 'error')
        return redirect(url_for('index'))

@app.route('/send-bulk-email', methods=['POST'])
def send_bulk_email():
    """Send bulk email to all contacts"""
    try:
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not subject or not message:
            flash('Subject and message are required!', 'error')
            return redirect(url_for('view_contacts'))
        
        contacts = db_manager.get_all_contacts()
        sent_count = 0
        failed_count = 0
        
        for contact in contacts:
            try:
                # Now contact is a Contact object
                if not contact.email:
                    failed_count += 1
                    continue
                
                msg = MIMEMultipart()
                msg['From'] = f"{EMAIL_CONFIG['FROM_NAME']} <{EMAIL_CONFIG['EMAIL']}>"
                msg['To'] = contact.email
                msg['Subject'] = subject
                
                html_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #667eea;">🎯 ToyCraft Tales</h1>
                            <p style="font-size: 18px; color: #666;">Hi {contact.name}! 👋</p>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 30px; border-radius: 15px; margin-bottom: 20px;">
                            {message.replace(chr(10), '<br>')}
                        </div>
                        
                        <div style="text-align: center; padding: 20px; background: #f8fafc; border-radius: 10px; margin-top: 20px;">
                            <p style="font-size: 14px; color: #999; margin: 0;">
                                © 2025 ToyCraft Tales. All rights reserved.
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                msg.attach(MIMEText(html_body, 'html'))
                
                server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
                server.starttls()
                server.login(EMAIL_CONFIG['EMAIL'], EMAIL_CONFIG['PASSWORD'])
                server.send_message(msg)
                server.quit()
                
                sent_count += 1
                print(f"📧 Email sent to {contact.email}")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to send email to {contact.email}: {e}")
        
        if sent_count > 0:
            flash(f'✅ Successfully sent {sent_count} emails! {failed_count} failed.', 'success')
        else:
            flash('❌ Failed to send any emails. Check your email configuration.', 'error')
            
    except Exception as e:
        print(f"❌ Error in bulk email: {e}")
        flash('Error sending bulk emails.', 'error')
    
    return redirect(url_for('view_contacts'))

@app.route('/api/contact-count')
def contact_count_api():
    """API endpoint to get contact count"""
    try:
        count = db_manager.get_contact_count()
        return jsonify({'count': count, 'status': 'success'})
    except Exception as e:
        print(f"❌ Error getting contact count: {e}")
        return jsonify({'count': 0, 'status': 'error'})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Add this route to app.py for testing
@app.route('/test-email')
def test_email():
    success = send_welcome_email("Prianshu", "jyosyulaprianshu@gmail.com")
    return f"Email test: {'Success' if success else 'Failed'}"

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/story')
def story():
    return render_template('story.html')

@app.route('/status')
def status():
    """System status page"""
    try:
        db_status = "Connected" if test_database_connection() else "Disconnected"
        contact_count = db_manager.get_contact_count()
        
        status_info = {
            'database': db_status,
            'contacts': contact_count,
            'ngrok_url': ngrok.tunnel_url if ngrok.ngrok_started else 'Not started',
            'local_ip': get_local_ip(),
            'email_configured': bool(EMAIL_CONFIG['EMAIL'] and EMAIL_CONFIG['PASSWORD'])
        }
        
        return jsonify(status_info)
    except Exception as e:
        return jsonify({'error': str(e)})

def start_ngrok_tunnel():
    """Start ngrok tunnel in background"""
    tunnel_url = ngrok.start_ngrok(5000)
    if tunnel_url:
        print("=" * 70)
        print("🌐 NGROK TUNNEL ACTIVE!")
        print("=" * 70)
        print(f"🔗 Public URL: {tunnel_url}")
        print(f"📤 Share this URL with anyone worldwide!")
        print(f"📊 Admin Panel: {tunnel_url}/contacts")
        print("=" * 70)
    else:
        print("❌ Ngrok not available - only local access")

def display_startup_info():
    """Display comprehensive startup information"""
    ip = get_local_ip()
    
    print("=" * 70)
    print("🎯 TOYCRAFT TALES DASHBOARD STARTING...")
    print("=" * 70)
    
    db_connected = test_database_connection()
    
    print(f"💻 Local Access:")
    print(f"   🏠 Homepage: http://127.0.0.1:5000")
    print(f"   📊 Dashboard: http://127.0.0.1:5000/dashboard")
    print(f"   📈 Charts: http://127.0.0.1:5000/charts")
    print(f"   📖 Story: http://127.0.0.1:5000/story")
    print(f"   📝 Admin: http://127.0.0.1:5000/contacts")
    
    print(f"\n📱 Network Access (Same WiFi):")
    print(f"   🌐 Homepage: http://{ip}:5000")
    print(f"   📊 Admin Panel: http://{ip}:5000/contacts")
    
    print(f"\n💾 Database Status:")
    print(f"   📊 MySQL: {'✅ Connected' if db_connected else '❌ Disconnected'}")
    print(f"   📝 Contact Count: {db_manager.get_contact_count() if db_connected else 'N/A'}")
    
    print(f"\n📧 Email Status:")
    email_configured = bool(EMAIL_CONFIG['EMAIL'] and EMAIL_CONFIG['PASSWORD'])
    print(f"   📧 Configuration: {'✅ Ready' if email_configured else '❌ Not configured'}")
    if not email_configured:
        print(f"   ⚠️  Update EMAIL_CONFIG in app.py to enable email features")
    
    print("=" * 70)

if __name__ == '__main__':
    try:
        display_startup_info()
        
        # Start ngrok tunnel in background thread
        ngrok_thread = threading.Thread(target=start_ngrok_tunnel, daemon=True)
        ngrok_thread.start()
        
        time.sleep(2)
        
        print("🚀 Starting Flask server...")
        print("🌍 ToyCraft Tales is now live!")
        print("\n" + "=" * 70)
        
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        ngrok.stop_tunnel()
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ STARTUP ERROR: {e}")
        ngrok.stop_tunnel()
        sys.exit(1)