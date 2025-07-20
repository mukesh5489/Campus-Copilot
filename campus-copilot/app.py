from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from assistant import ask_ai
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from email_sender import send_email
from google_auth_oauthlib.flow import Flow
from supabase_client import add_event
import os
from calendar_sync import authenticate_google_calendar, create_event


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your-secret-key"  # Set a secure secret key
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6), nullable=True)
    role = db.Column(db.String(20), default='student')
    is_active = db.Column(db.Boolean, default=True)

# User activity log model
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

scheduler = BackgroundScheduler()
scheduler.start()

CLIENT_SECRETS_FILE = "client_secret_473554082810-u3cjeo77vs0tgkn1kld88pd1gel25ofa.apps.googleusercontent.com.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = 'http://localhost:5000/oauth2callback'

def schedule_email(event):
    # event: dict with 'email', 'title', 'description', 'datetime'
    send_time = event['datetime'] - timedelta(minutes=30)
    scheduler.add_job(
        send_email,
        'date',
        run_date=send_time,
        args=[event['email'], f"Upcoming: {event['title']}", event['description']]
    )

@app.route('/')
def index():
    # Fetch events from Supabase
    from supabase_client import supabase
    response = supabase.table("events").select("title,category,description,event_date,event_time").execute()
    events = []
    if response.data:
        for ev in response.data:
            events.append({
                "title": ev["title"],
                "start": f"{ev['event_date']}T{ev['event_time']}",
                "description": ev["description"],
                "category": ev["category"]
            })
    return render_template('index.html', events=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Log login activity
            db.session.add(UserActivity(user_id=user.id, action='login'))
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    import random
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form.get('role', 'student')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            otp = str(random.randint(100000, 999999))
            user = User(username=username, password=hashed_password, email=email, is_verified=False, otp=otp, role=role)
            db.session.add(user)
            db.session.commit()
            send_email(email, "Campus Copilot Email Verification", f"Your verification code is: {otp}")
            flash('Account created! Please check your email for the verification code.', 'success')
            return redirect(url_for('verify', username=username))
    return render_template('signup.html')
# Role-based access decorator
from functools import wraps
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Access denied.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Example admin-only route
@app.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    return render_template('admin.html')
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('signup'))
    if request.method == 'POST':
        otp_input = request.form['otp']
        if user.otp == otp_input:
            user.is_verified = True
            user.otp = None
            db.session.commit()
            flash('Email verified! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification code.', 'danger')
    return render_template('verify.html', username=username)

@app.route('/dashboard')
@login_required
def dashboard():
    # Event filtering and search
    category = request.args.get('category')
    search = request.args.get('search')
    from supabase_client import supabase
    query = supabase.table("events").select("title,category,description,event_date,event_time")
    if category:
        query = query.eq("category", category)
    if search:
        query = query.ilike("title", f"%{search}%")
    response = query.execute()
    events = []
    if response.data:
        for ev in response.data:
            events.append({
                "title": ev["title"],
                "date": ev["event_date"],
                "time": ev["event_time"],
                "description": ev["description"],
                "category": ev["category"]
            })
    return render_template('dashboard.html', events=events, category=category, search=search)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_event', methods=['GET', 'POST'])
def add_event_route():
    if request.method == 'POST':
        event = {
            'title': request.form['title'],
            'description': request.form['description'],
            'category': request.form['category'],
            'date': request.form['date'],
            'time': request.form['time'],
            'email': request.form.get('email', 'default@email.com'),
            'approved': False  # New events require admin approval
        }
        add_event(event)
        # Log event creation
        if current_user.is_authenticated:
            db.session.add(UserActivity(user_id=current_user.id, action='create_event'))
            db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_event.html')

@app.route('/notice_board')
def notice_board():
    # Fetch notices from Supabase (category = 'notice')
    from supabase_client import supabase
    response = supabase.table("events").select("title,description,event_date,event_time").eq("category", "notice").execute()
    notices = []
    if response.data:
        for n in response.data:
            notices.append({
                "title": n["title"],
                "description": n["description"],
                "date": n["event_date"],
                "time": n["event_time"]
            })
    return render_template('notice_board.html', notices=notices)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['question']
    response = ask_ai(user_input)
    return response

@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    session['flow'] = flow  # Store flow in session if needed
    return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Save credentials to token.json for later use
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())
    return "Google Calendar synced!"

# Add approval field to events table in Supabase
# (Assume events table has 'approved' boolean field)

@app.route('/admin/events', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_events():
    from supabase_client import supabase
    # Bulk delete
    if request.method == 'POST' and 'bulk_delete' in request.form:
        ids = request.form.getlist('bulk_event_ids')
        for event_id in ids:
            supabase.table('events').delete().eq('id', event_id).execute()
        flash(f'{len(ids)} events deleted.', 'success')
    # Bulk approve
    if request.method == 'POST' and 'bulk_approve' in request.form:
        ids = request.form.getlist('bulk_event_ids')
        for event_id in ids:
            supabase.table('events').update({'approved': True}).eq('id', event_id).execute()
        flash(f'{len(ids)} events approved.', 'success')
    # Handle event approval
    if request.method == 'POST' and 'approve_event_id' in request.form:
        event_id = request.form['approve_event_id']
        supabase.table('events').update({'approved': True}).eq('id', event_id).execute()
        flash('Event approved.', 'success')
    # Handle event deletion
    if request.method == 'POST' and 'delete_event_id' in request.form:
        event_id = request.form['delete_event_id']
        supabase.table('events').delete().eq('id', event_id).execute()
        flash('Event deleted.', 'success')
    # Handle event editing
    if request.method == 'POST' and 'edit_event_id' in request.form:
        event_id = request.form['edit_event_id']
        update_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'category': request.form['category'],
            'event_date': request.form['date'],
            'event_time': request.form['time'],
            'user_email': request.form['email']
        }
        supabase.table('events').update(update_data).eq('id', event_id).execute()
        flash('Event updated.', 'success')
    # Handle event addition
    if request.method == 'POST' and 'add_event' in request.form:
        new_event = {
            'title': request.form['title'],
            'description': request.form['description'],
            'category': request.form['category'],
            'event_date': request.form['date'],
            'event_time': request.form['time'],
            'user_email': request.form['email']
        }
        supabase.table('events').insert(new_event).execute()
        flash('Event added.', 'success')
    # Export events as CSV
    if request.method == 'POST' and 'export_events' in request.form:
        import csv
        from io import StringIO
        response = supabase.table('events').select('*').execute()
        events = response.data if response.data else []
        si = StringIO()
        cw = csv.writer(si)
        if events:
            cw.writerow(events[0].keys())
            for e in events:
                cw.writerow([e[k] for k in events[0].keys()])
        output = si.getvalue()
        return output, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=events.csv'}
    # Fetch all events
    response = supabase.table('events').select('*').execute()
    events = response.data if response.data else []
    # Analytics: count events by category
    from collections import Counter
    category_counts = Counter([e['category'] for e in events])
    total_events = len(events)
    approved_events = sum(1 for e in events if e.get('approved'))
    pending_events = total_events - approved_events
    return render_template('admin_events.html', events=events, category_counts=category_counts, total_events=total_events, approved_events=approved_events, pending_events=pending_events)
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_users():
    # Bulk actions
    if request.method == 'POST' and 'bulk_delete' in request.form:
        ids = request.form.getlist('bulk_user_ids')
        for user_id in ids:
            User.query.filter_by(id=user_id).delete()
        db.session.commit()
        flash(f'{len(ids)} users deleted.', 'success')
    if request.method == 'POST' and 'bulk_activate' in request.form:
        ids = request.form.getlist('bulk_user_ids')
        for user_id in ids:
            user = User.query.get(user_id)
            if user:
                user.is_active = True
        db.session.commit()
        flash(f'{len(ids)} users activated.', 'success')
    if request.method == 'POST' and 'bulk_deactivate' in request.form:
        ids = request.form.getlist('bulk_user_ids')
        for user_id in ids:
            user = User.query.get(user_id)
            if user:
                user.is_active = False
        db.session.commit()
        flash(f'{len(ids)} users deactivated.', 'success')
    # Handle user deletion
    if request.method == 'POST' and 'delete_user_id' in request.form:
        user_id = request.form['delete_user_id']
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
        flash('User deleted.', 'success')
    # Handle user editing
    if request.method == 'POST' and 'edit_user_id' in request.form:
        user_id = request.form['edit_user_id']
        user = User.query.get(user_id)
        if user:
            user.username = request.form['username']
            user.email = request.form['email']
            user.role = request.form['role']
            user.is_active = 'is_active' in request.form
            db.session.commit()
            flash('User updated.', 'success')
    # Handle user addition
    if request.method == 'POST' and 'add_user' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        is_active = 'is_active' in request.form
        user = User(username=username, email=email, password=password, role=role, is_verified=True, is_active=is_active)
        db.session.add(user)
        db.session.commit()
        flash('User added.', 'success')
    # Handle password reset
    if request.method == 'POST' and 'reset_password_id' in request.form:
        user_id = request.form['reset_password_id']
        new_password = generate_password_hash(request.form['new_password'])
        user = User.query.get(user_id)
        if user:
            user.password = new_password
            db.session.commit()
            flash('Password reset.', 'success')
    # Handle role change
    if request.method == 'POST' and 'change_role_id' in request.form:
        user_id = request.form['change_role_id']
        new_role = request.form['new_role']
        user = User.query.get(user_id)
        if user:
            user.role = new_role
            db.session.commit()
            flash('User role updated.', 'success')
    # Handle activate/deactivate
    if request.method == 'POST' and 'activate_user_id' in request.form:
        user_id = request.form['activate_user_id']
        user = User.query.get(user_id)
        if user:
            user.is_active = True
            db.session.commit()
            flash('User activated.', 'success')
    if request.method == 'POST' and 'deactivate_user_id' in request.form:
        user_id = request.form['deactivate_user_id']
        user = User.query.get(user_id)
        if user:
            user.is_active = False
            db.session.commit()
            flash('User deactivated.', 'success')
    # Export users as CSV
    if request.method == 'POST' and 'export_users' in request.form:
        import csv
        from io import StringIO
        users = User.query.all()
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['id', 'username', 'email', 'role', 'is_active'])
        for u in users:
            cw.writerow([u.id, u.username, u.email, u.role, u.is_active])
        output = si.getvalue()
        return output, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=users.csv'}
    # View user activity log
    activity_log = UserActivity.query.order_by(UserActivity.timestamp.desc()).limit(100).all()
    users = User.query.all()
    return render_template('admin_users.html', users=users, activity_log=activity_log)

# Create default admin user if not exists
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@campus.com',
            password=generate_password_hash('admin2025'),
            role='admin',
            is_verified=True
        )
        db.session.add(admin_user)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)