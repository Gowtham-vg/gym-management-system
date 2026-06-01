import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector

from flask_bcrypt import Bcrypt

from werkzeug.utils import secure_filename
from flask import jsonify, request

import random
import string
from flask_mail import Mail, Message

import json

 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime, timedelta
from flask import session

from flask import send_from_directory

from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import mysql.connector


 
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv('SECRET_KEY', 'dev_fallback_key')
bcrypt = Bcrypt(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads' # type: ignore

# Email settings (for sending OTP emails)

app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('BREVO_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)
 
# Folder to store uploaded images
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Add more formats if needed


# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv('DB_PASSWORD'),
        database="gym_management"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login_option')
def login_option():
    return render_template('login_option.html')

 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, name, password FROM members WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.check_password_hash(user['password'], password):
                session['user_id'] = user['id']  # Store user ID in the session
                session['user_name'] = user['name']  # Store user name for personalized greeting
                flash("Login successful!", "success")
                return redirect(url_for('user_dashboard'))
            else:
                flash("Invalid username or password.", "error")
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']  # ✅ Getting email from form
        gender = request.form['gender']
        age = request.form['age']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect('/register')

        # Validate email format (only @gmail.com allowed)
        if not email.endswith("@gmail.com"):
            flash('Please enter a valid Gmail address!', 'error')
            return redirect('/register')

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # ✅ Insert into database with email field
            sql = """
                INSERT INTO members (name, username, email, password, gender, age, mobile, role, membership_plan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'user', 'Basic')
            """
            cursor.execute(sql, (name, username, email, hashed_password, gender, age, mobile))
            connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect('/login')
        except mysql.connector.Error as e:
            flash(f'Error: {e}', 'error')
        finally:
            cursor.close()
            connection.close()

    return render_template('register.html')

 

def send_email_otp(email, otp):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('GMAIL_APP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "OTP for Password Reset"

    body = f"Your OTP for password reset is: {otp}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print(f"✅ OTP Sent Successfully to {email}!")
    except Exception as e:
        print(f"❌ Error Sending Email: {e}")


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        mobile = request.form['mobile']
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if username & mobile match
        cursor.execute("SELECT * FROM members WHERE username = %s AND mobile = %s", (username, mobile))
        user = cursor.fetchone()

        if user:
            # Update email in database
            cursor.execute("UPDATE members SET email = %s WHERE username = %s", (email, username))
            conn.commit()

            # Generate OTP
            otp = random.randint(100000, 999999)
            cursor.execute("UPDATE members SET otp = %s WHERE username = %s", (otp, username))
            conn.commit()
            conn.close()

            # Send OTP to new email
            send_email_otp(email, otp)

            session['username'] = username  # Store username in session
            session['email'] = email        # Store email in session

            return redirect(url_for('verify_otp'))
        else:
            flash("Invalid username or mobile number", "error")
            conn.close()
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        username = session.get('username')
        entered_otp = request.form['otp']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT otp FROM members WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and str(user['otp']) == entered_otp:
            session['otp_verified'] = True
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP", "error")
            conn.close()
            return redirect(url_for('verify_otp'))

    return render_template('verify_otp.html', username=session.get('username'), email=session.get('email'))

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified'):
        return redirect(url_for('forgot_password'))  # Redirect if OTP is not verified

    if request.method == 'POST':
        username = session.get('username')
        new_password = request.form['new_password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE members SET password = %s, otp = NULL WHERE username = %s", (new_password, username))
        conn.commit()
        conn.close()

        session.clear()  # Clear session after password reset
        flash("Password updated successfully!", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', username=session.get('username'))

@app.route("/payment")
def payment_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Fetch plan details from DB
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name, price FROM plans")
    plans = cursor.fetchall()
    cursor.close()

    # 🔥 Database Connection
    conn = get_db_connection()
    cursor = conn.cursor()

    return render_template("payment.html", plans=plans)

 

@app.route("/store_payment", methods=["POST"])
def store_payment():
    if "user_id" not in session:
        return "User not logged in!", 403  # ❌ Not logged in

    user_id = session["user_id"]
    selected_plan = request.form["plan"]  # 🔥 Get selected plan

    # 🔥 Database Connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Get Plan Price
    cursor.execute("SELECT price FROM plans WHERE name = %s", (selected_plan,))
    plan_data = cursor.fetchone()
    
    if not plan_data:
        cursor.close()
        conn.close()
        return "Invalid plan selected!", 400  # ❌ If plan not found, reject

    amount = plan_data[0]  # Get price from DB

    # 🔥 Update User Membership
    today = datetime.today().date()
    renewal_date = today + timedelta(days=30)

    cursor.execute("""
        UPDATE members 
        SET last_payment_date = %s, next_renewal_date = %s, membership_plan = %s 
        WHERE id = %s
    """, (today, renewal_date, selected_plan, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Payment of ₹{amount} successful! Plan updated to {selected_plan}. Next renewal on {renewal_date}.", "success")
    return redirect(url_for("user_dashboard"))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Query the database to verify the admin
            cursor.execute("SELECT password FROM admin WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result and bcrypt.check_password_hash(result[0], password):
                flash("Admin login successful!", "success")
                return redirect(url_for('admin_dashboard'))  # Redirect to dashboard on successful login
            else:
                flash("Invalid username or password!", "error")
        finally:
            cursor.close()
            connection.close()

    return render_template('admin_login.html')

 
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash("Please log in to access your dashboard.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT name FROM members WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            flash("User not found!", "error")
            return redirect(url_for('login'))

        session['user_name'] = user['name']  # Ensure session stores user_name

        return render_template(
            'user_dashboard.html',
            user_name=user['name']  # Pass user_name to template
        )
    finally:
        cursor.close()
        connection.close()





@app.route('/workout_plans')
def workout_plans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT id, name, description, exercises, frequency FROM workout_plans')
    workouts = cursor.fetchall()

    conn.close()
    
    return render_template('workout_plans.html', workouts=workouts)



@app.route('/workout_details/<int:workout_id>')
def workout_details(workout_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch workout details
    cursor.execute("SELECT * FROM workout_plans WHERE id = %s", (workout_id,))
    workout = cursor.fetchone()

    # Fetch all videos for this workout
    cursor.execute("SELECT video_url FROM workout_videos WHERE workout_id = %s", (workout_id,))
    videos = cursor.fetchall()  # Fetch multiple videos

    conn.close()

    if workout:
        video_urls = [video['video_url'] for video in videos]  # Extract all video URLs
        print("DEBUG: Video URLs fetched from database ->", video_urls)  # Debugging
        return render_template('workout_details.html', workout=workout, video_urls=video_urls)
    else:
        return "Workout not found", 404

    

@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('static/videos', filename, mimetype='video/mp4')









@app.route('/diet_plans')
def diet_plans():
    return render_template('diet_plans.html')


@app.route('/get_plans')
def get_plans():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT name, price FROM plans")
        plans = cursor.fetchall()
        return jsonify(plans)
    finally:
        cursor.close()
        connection.close()

@app.route('/get_sessions', methods=['GET'])
def get_sessions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT sessions.id, users.name, sessions.session_name, sessions.session_time, sessions.session_date, sessions.instructor 
        FROM sessions JOIN users ON sessions.user_id = users.id
    """)
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(sessions)



@app.route("/book_session", methods=["GET", "POST"])
def book_session():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor.execute("SELECT name, email, mobile FROM members WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if request.method == "GET":
        session_data = request.args.get("session", "{}")
        session_details = json.loads(session_data)
        return render_template("book_session.html", session=session_details, user=user)

    elif request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # ✅ Fetch user details (including first_name & email)
    cursor.execute("SELECT name AS first_name, email, mobile FROM members WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return "User not found", 400  # Handle missing user case

    first_name = user["first_name"]
    email = user["email"]
    phone = user["mobile"]
    session_name = request.form.get("session_name")
    session_time = request.form.get("session_time")
    session_date = request.form.get("session_date")
    instructor = request.form.get("instructor")
    message = request.form.get("message", "").strip()

    if not message:
        message = "No message provided"

    # ✅ Insert full session details including first_name, email, and phone
    cursor.execute(
        """
        INSERT INTO session_bookings (first_name, email, phone, user_id, session_name, session_time, session_date, instructor, message, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Active')
        """,
        (first_name, email, phone, user_id, session_name, session_time, session_date, instructor, message),
    )
    conn.commit()
    conn.close()

        # ✅ Return JSON response for popup
    return jsonify({
            "success": True,
            "message": "You booked this session successfully!",
            "user_name": first_name,
            "email": email,
            "phone": phone,
            "session_name": session_name,
            "session_time": session_time,
            "session_date": session_date,
            "instructor": instructor,
        })

    return redirect(url_for("session_details"))


def extract_session_details(session_string):
    """Extracts session details safely from session string"""
    try:
        parts = session_string.split(" - ")
        if len(parts) < 2:
            return "Unknown", "Unknown", "Unknown", "Unknown"

        session_name = parts[0]
        time_and_date = parts[1].split(" on ")
        if len(time_and_date) < 2:
            return "Unknown", "Unknown", "Unknown", "Unknown"

        session_time = time_and_date[0]
        date_and_instructor = time_and_date[1].split(" with ")
        if len(date_and_instructor) < 2:
            return "Unknown", "Unknown", "Unknown", "Unknown"

        session_date = date_and_instructor[0]
        instructor = date_and_instructor[1]

        return session_name, session_time, session_date, instructor

    except IndexError:
        return "Unknown", "Unknown", "Unknown", "Unknown"



@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))





@app.route("/session_details")
def session_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT session_day, session_name, session_time, session_date, instructor FROM sessions"
    cursor.execute(query)
    sessions = cursor.fetchall()
    
    conn.close()
    
    # Debugging: Check if Friday is retrieved
    print("Fetched Sessions:", sessions)
    
    return render_template("session_details.html", sessions=sessions)


@app.route('/cancel_session/<int:session_id>', methods=['POST'])
def cancel_session(session_id):
    if 'user_id' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Move session to cancelled_sessions
        cursor.execute("""
            INSERT INTO cancelled_sessions (user_id, session_name, session_time, session_date, instructor)
            SELECT user_id, session_name, session_time, session_date, instructor 
            FROM session_bookings WHERE id = %s
        """, (session_id,))

        # Update session status instead of deleting
        cursor.execute("UPDATE session_bookings SET status = 'Cancelled' WHERE id = %s", (session_id,))

        conn.commit()
        flash("Session cancelled successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('session_details'))







@app.route('/progress_tracking')
def progress_tracking():
    return render_template('progress_tracking.html')

def generate_progress_pdf(user_id):
    try:
        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user details
        cursor.execute("SELECT name, email FROM members WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        # Fetch progress data
        cursor.execute("SELECT * FROM progress_tracking WHERE user_id = %s", (user_id,))
        progress = cursor.fetchall()

        if not user or not progress:
            return None  # If no data, return nothing

        # Create PDF File
        pdf_path = f"static/reports/progress_report_{user_id}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 14)

        # PDF Content
        c.drawString(100, 750, f"Progress Report - {user['name']}")
        c.drawString(100, 730, f"Email: {user['email']}")
        c.drawString(100, 710, f"User ID: {user_id}")

        # Table Header
        y = 680
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "Workout Type")
        c.drawString(300, y, "Duration (mins)")
        c.drawString(450, y, "Calories Burned")

        y -= 10
        c.line(50, y, 550, y)
        y -= 20
        c.setFont("Helvetica", 11)

        # Add progress data with fixed alignment
        for row in progress:
            workout = row['workout_type']
            duration = str(row['duration'])
            calories = str(row['calories_burned'])

            c.drawString(60, y, workout)
            c.drawRightString(370, y, duration)     # right-aligned for numbers
            c.drawRightString(520, y, calories)     # right-aligned for numbers

            y -= 20


        # Save PDF
        c.save()

        # Store PDF Path in DB
        cursor.execute("""
            INSERT INTO progress_reports (user_id, user_name, email, pdf_path, sent_status)
            VALUES (%s, %s, %s, %s, 'Pending')
            ON DUPLICATE KEY UPDATE pdf_path = VALUES(pdf_path), sent_status = 'Pending'
        """, (user_id, user['name'], user['email'], pdf_path))

        conn.commit()
        cursor.close()
        conn.close()

        return pdf_path  # Return path for download

    except Exception as e:
        print("Error generating PDF:", e)
        return None
    

@app.route('/download_progress_report')
def download_progress_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user_id = session['user_id']
    pdf_path = generate_progress_pdf(user_id)  # Generate the report

    if pdf_path and os.path.exists(pdf_path):  # Check if PDF is created
        return send_file(pdf_path, as_attachment=True)
    else:
        flash("No progress data available for download.", "error")
        return redirect(url_for('progress_tracking'))


from datetime import datetime
 



@app.route("/get_workout_progress")
def get_workout_progress():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 403

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # ✅ Aggregate calories and duration per workout_date
        cursor.execute("""
            SELECT 
                workout_date, 
                workout_type, 
                SUM(duration) AS total_duration, 
                SUM(calories_burned) AS total_calories
            FROM progress_tracking
            WHERE user_id = %s AND calories_burned IS NOT NULL
            GROUP BY workout_date, workout_type
            ORDER BY workout_date ASC
        """, (user_id,))
        workout_data = cursor.fetchall()

        # ✅ Fix date format for JSON response
        for workout in workout_data:
            workout["workout_date"] = workout["workout_date"].strftime("%Y-%m-%d")

    finally:
        cursor.close()
        conn.close()

    if not workout_data:
        return jsonify({"message": "No progress found", "workout_data": []})

    return jsonify({"workout_data": workout_data})

from flask import request, jsonify
import mysql.connector
from datetime import datetime

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        feedback_text = data.get('feedback')
        user_name = data.get('user_name')  

        if not feedback_text or not user_name:
            return jsonify({"message": "Invalid input"}), 400

        conn = get_db_connection()  # Use consistent connection method
        cursor = conn.cursor()

        query = "INSERT INTO feedback (user_name, feedback_text, created_at) VALUES (%s, %s, NOW())"
        cursor.execute(query, (user_name, feedback_text))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Feedback submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_feedback')
def get_feedback():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT user_name, feedback_text, created_at FROM feedback ORDER BY created_at DESC LIMIT 10")
        feedbacks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(feedbacks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html')  # Make sure this matches!










 
 #----session card
@app.route('/user_sessions')
def user_sessions():
    if 'user_id' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, session_name, session_time, session_date, instructor, status
            FROM session_bookings
            WHERE user_id = %s
        """, (user_id,))
        sessions = cursor.fetchall()

        # Debugging: Check if ID is retrieved
        print("Fetched Sessions:", sessions)
    finally:
        cursor.close()
        conn.close()

    return render_template("session_details.html", sessions=sessions)

@app.route('/get_user_sessions')
def get_user_sessions():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 403

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, session_name, session_time, session_date, instructor, status
            FROM session_bookings
            WHERE user_id = %s
        """, (user_id,))
        sessions = cursor.fetchall()

        # 🔥 Debugging: Print fetched sessions
        print("DEBUG: Fetched Sessions ->", sessions)

    finally:
        cursor.close()
        conn.close()

    return jsonify(sessions)


@app.route('/get_workout_plans')
def get_workout_plans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name FROM workout_plans")
        workout_plans = cursor.fetchall()
        return jsonify(workout_plans)
    finally:
        cursor.close()
        conn.close()


@app.route('/start_workout/<int:workout_id>')
def start_workout(workout_id):
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 403

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch user details
        cursor.execute("SELECT name, age, membership_plan, mobile FROM members WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        # Fetch workout details
        cursor.execute("SELECT name, exercises, description FROM workout_plans WHERE id = %s", (workout_id,))
        workout = cursor.fetchone()

        if not user or not workout:
            return jsonify({"error": "User or Workout not found"}), 404

        return jsonify({"user": user, "workout": workout})
    finally:
        cursor.close()
        conn.close()


@app.route('/submit_exercise', methods=['POST'])
def submit_exercise():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 403

    data = request.json
    user_id = session['user_id']
    workout_id = data.get("workout_id")
    exercise_name = data.get("exercise")
    sets_completed = data.get("sets")
    reps_completed = data.get("reps")
    workout_date = datetime.today().strftime('%Y-%m-%d')  # ✅ Ensure workout date is included

    if not (workout_id and exercise_name and sets_completed and reps_completed):
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # ✅ Fetch only `name` from `workout_plans`
        cursor.execute("SELECT name FROM workout_plans WHERE id = %s", (workout_id,))
        workout_details = cursor.fetchone()

        if not workout_details:
            return jsonify({"error": "Workout plan not found"}), 404

        workout_type = workout_details["name"]

        # ✅ Auto-generate duration & calories_burned
        workout_defaults = {
            "Dynamic Movement Training": (45, 350),
            "Freestyle Group Training": (50, 400),
            "Les Mills BODYPUMP": (60, 500),
            "Les Mills BODYBALANCE": (40, 250),
            "Les Mills BODYCOMBAT": (55, 550),
            "One-on-One Personal Training": (60, 600)
        }

        # ✅ Assign values based on workout type, or set defaults if not found
        duration, calories_burned = workout_defaults.get(workout_type, (30, 200))  

        # ✅ Insert into progress_tracking
        cursor.execute("""
            INSERT INTO progress_tracking 
            (user_id, workout_date, workout_type, duration, calories_burned, workout_id, exercise_name, sets_completed, reps_completed, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            user_id, workout_date, workout_type, duration, calories_burned,
            workout_id, exercise_name, sets_completed, reps_completed
        ))

        conn.commit()
        return jsonify({"success": True, "message": f"{exercise_name} progress saved!"})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        cursor.close()
        conn.close()














@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        mobile = request.form['mobile']
        password = request.form['password']
        security_key = request.form['security_key']

        if security_key != os.getenv('ADMIN_SECURITY_KEY', '8888'):
            flash("Security key is incorrect!", "error")
            return redirect('/admin/register')

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Insert into admin table
            sql = """
                INSERT INTO admin (name, username, password, mobile)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (name, username, hashed_password, mobile))
            connection.commit()
            flash("Admin registered successfully! Please log in.", "success")
            return redirect('/admin/login')
        except mysql.connector.Error as e:
            flash(f'Error: {e}', "error")
        finally:
            cursor.close()
            connection.close()

    return render_template('admin_register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/add_remove_members', methods=['GET', 'POST'])
def add_remove_members():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name, username, gender, age, mobile FROM members")
        users = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('add_remove_members.html', users=users)

@app.route('/remove_members', methods=['POST'])
def remove_members():
    selected_members = request.form.getlist('selected_members')

    if not selected_members:
        flash("No members selected for removal.", "error")
        return redirect(url_for('add_remove_members'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Convert the list of IDs into a tuple for the SQL query
        cursor.execute("DELETE FROM members WHERE id IN (%s)" % ','.join(['%s'] * len(selected_members)), tuple(selected_members))
        connection.commit()
        flash("Selected members removed successfully.", "success")
    except mysql.connector.Error as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('add_remove_members'))

 
@app.route('/edit_member', methods=['POST'])
def edit_member():
    user_id = request.form['id']
    name = request.form['name']
    username = request.form['username']
    gender = request.form['gender']
    age = request.form['age']
    mobile = request.form['mobile']

    # Corrected connection using mysql.connector
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Update the user data in the database
        cursor.execute("""
            UPDATE members SET name=%s, username=%s, gender=%s, age=%s, mobile=%s WHERE id=%s
        """, (name, username, gender, age, mobile, user_id))
        connection.commit()

        flash('Member details updated successfully!', 'success')
    except mysql.connector.Error as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect('/add_remove_members')

@app.route('/view_users')
def view_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name, username, gender, age, mobile FROM members")
        users = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('view_users.html', users=users)

@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        # Get form data
        category = request.form.get('category')
        name = request.form.get('name')
        description = request.form.get('description')
        specification = request.form.get('specification')
        price = request.form.get('price')
        
        # Handle file upload
        image = request.files['image']
        
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

            # Save the image to the specified folder
            image.save(image_path)
            image_url = f"uploads/{image_filename}"  # Save the relative URL for the image
        else:
            image_url = None

        # Insert into database
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            query = """INSERT INTO equipment (category, name, description, specification, price, image_url)
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            values = (category, name, description, specification, price, image_url)

            cursor.execute(query, values)
            connection.commit()

            flash("Equipment added successfully!", "success")
            return redirect(url_for('equipment'))
        except mysql.connector.Error as e:
            flash(f'Error: {e}', 'error')
        finally:
            cursor.close()
            connection.close()

    return render_template('add_equipment.html')

@app.route('/equipment')
def equipment():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM equipment")
        items = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('equipment.html', items=items)

 

@app.route('/get_products_by_category', methods=['GET'])
def get_products_by_category():
    category = request.args.get('category')
    
    # Establish a new database connection
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Fetch products based on category
        if category == 'All':
            query = "SELECT * FROM equipment"
            cursor.execute(query)
        else:
            query = "SELECT * FROM equipment WHERE category = %s"
            cursor.execute(query, (category,))
        
        products = cursor.fetchall()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        db.close()
    
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # ✅ Prevents duplicate Flask processes



