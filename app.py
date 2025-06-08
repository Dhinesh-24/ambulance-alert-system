from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
import mysql.connector
from dotenv import load_dotenv
import os
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from traffic_analyzer import analyze_traffic
from ultralytics import YOLO
import cv2

#1 in new.py
#import gdown 

#model_path = "best.pt" 
#if not os.path.exists(model_path):
#    gdown.download("https://drive.google.com/uc?export=download&id=11pqvlzyayo1ttqDc73J2r8qT2EeSAXz5", model_path, quiet=False)
#1 in new.py

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )


def send_discord_webhook(webhook_url, message):
    if not webhook_url:
        print("Webhook URL not configured.")
        return False
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(webhook_url, json=data, headers=headers)
        if response.status_code in (200, 204):
            print(f"Webhook sent successfully: Status code {response.status_code}")
            return True
        else:
            print(f"Failed to send webhook. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception sending webhook: {e}")
        return False


def send_alert_to_police(message):
    webhook_url = os.getenv('POLICE_WEBHOOK')
    if not webhook_url:
        print("Police webhook URL not found in environment.")
        return False
    return send_discord_webhook(webhook_url, message)


def send_alert_to_hospital(message):
    webhook_url = os.getenv('HOSPITAL_WEBHOOK')
    if not webhook_url:
        print("Hospital webhook URL not found in environment.")
        return False
    return send_discord_webhook(webhook_url, message)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password_raw = request.form.get('password')

        if not username or not email or not password_raw:
            flash("Please fill out all fields.", "error")
            return redirect(request.url)

        password = generate_password_hash(password_raw)

        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, password))
            db.commit()
        except mysql.connector.Error as err:
            db.rollback()
            flash(f"Database error: {err}", "error")
            return redirect(request.url)
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Please fill out all fields.", "error")
            return redirect(request.url)

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = 'user'
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session and session.get('user_type') == 'user':
        return render_template('dashboard.html', username=session.get('username'))
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/api/ambulance-location')
def ambulance_location():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT latitude, longitude FROM driver_locations ORDER BY updated_at DESC LIMIT 1")
    loc = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify(loc or {})


@app.route('/alert_police', methods=['POST'])
def alert_police_route():
    if 'user_id' not in session:
        return "Unauthorized", 401

    route_from = request.form.get('route_from', 'Unknown')
    route_to = request.form.get('route_to', 'Unknown')

    police_msg = (
        f"🚨 Ambulance is currently en route from **{route_from}** to **{route_to}**. "
        f"Please clear the way immediately."
    )

    hospital_msg = (
        f"🚑 Ambulance is on its way from **{route_from}** to **{route_to}**. "
        f"Prepare emergency services."
    )

    try:
        sent_police = send_alert_to_police(police_msg)
        sent_hospital = send_alert_to_hospital(hospital_msg)

        if sent_police and sent_hospital:
            flash("Alerts sent successfully to police and hospital!", "success")
        else:
            flash("Failed to send some alerts. Check logs.", "error")
    except Exception as e:
        print(f"Error sending alerts: {e}")
        flash("Failed to send alerts.", "error")

    if session.get('user_type') == 'driver':
        return redirect(url_for('driver_dashboard'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/api/nearest_hospital')
def api_nearest_hospital():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, latitude, longitude FROM hospital LIMIT 1")
    hospital = cursor.fetchone()
    cursor.close()
    db.close()
    if hospital:
        return jsonify(hospital)
    else:
        return jsonify({}), 404


# YOLO model load
model = YOLO("best.pt")  # Your trained model path os.getenv("YOLO_MODEL_PATH")

#2
#model = YOLO(model_path)

@app.route('/traffic_status')
def traffic_status():
    video_path = "static/traffic.mp4"
    frame_path = "static/frame_test.jpg"
    result = analyze_traffic(video_path, frame_path)
    return jsonify(result)


if __name__ == '__main__':
    print(app.url_map)  # debug: show all routes
    app.run(debug=True)
