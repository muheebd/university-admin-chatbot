import os
import sqlite3
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from flask import Flask, render_template, request, jsonify, session
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Secret key is loaded from the .env file - never hardcoded in source code.
# If the key is missing, raise a clear error immediately on startup.
secret_key = os.environ.get("FLASK_SECRET_KEY")
if not secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is not set. Please add it to your .env file.")
app.secret_key = secret_key

# 1. Load AI model, tokenizer and intents from the shared predictor module
from predictor import predict_intent, get_text_response, intents_data, CONFIDENCE_THRESHOLD

# 2. Database Helper Function
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('university.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# 3. Action Handlers (The magic that talks to the database)
def handle_database_action(action_tag, matric_no):
    if action_tag == "check_fees":
        finance = query_db('SELECT * FROM finances WHERE matric_no = ?', [matric_no], one=True)
        if finance:
            return (f"Your total billed fees are ₦{finance['total_billed']:,.2f}. "
                    f"You have paid ₦{finance['amount_paid']:,.2f}. "
                    f"Your outstanding balance is ₦{finance['balance']:,.2f}. "
                    f"Clearance Status: {finance['clearance_status']}.")
        return "I could not find a fee record for your account. Please visit the Bursary office."
    
    elif action_tag == "check_results":
        result = query_db('SELECT * FROM results WHERE matric_no = ? ORDER BY session DESC LIMIT 1', [matric_no], one=True)
        if result:
            return f"For the {result['session']} {result['semester']}, your GPA was {result['gpa']}. Your current Cumulative CGPA is {result['cgpa']}."

    elif action_tag == "check_accommodation":
        hostel = query_db('SELECT * FROM accommodation WHERE matric_no = ?', [matric_no], one=True)
        if hostel:
            return f"Your accommodation status: {hostel['status']}. You are assigned to {hostel['hostel_name']}, {hostel['room_number']}."
            
    elif action_tag == "check_courses":
        courses = query_db('SELECT * FROM course_registration WHERE matric_no = ?', [matric_no])
        if courses:
            course_list = ", ".join([c['course_code'] for c in courses])
            return f"You are currently registered for: {course_list}."

    elif action_tag == "check_payment_history":
        payment = query_db('SELECT * FROM payments_history WHERE matric_no = ? ORDER BY date DESC LIMIT 1', [matric_no], one=True)
        if payment:
            return f"Your last transaction was on {payment['date']}. Amount: ₦{payment['amount']:,.2f} for {payment['payment_type']}. Receipt No: {payment['receipt_no']}. Status: {payment['status']}."

    return "I couldn't find those specific records for your account. Please visit the admin office."

# 4. Deep Learning Prediction Logic
def get_bot_response(user_text):
    if not user_text or not user_text.strip():
        return "Please enter a valid question."

    # --- SESSION MANAGEMENT: Check if the bot is currently waiting for login details ---
    if session.get('awaiting_login'):
        # Expecting format: MatricNo, PIN (e.g., 22/03CYB059, 1234)
        parts = user_text.split(',')
        if len(parts) == 2:
            matric_no = parts[0].strip().upper()
            pin = parts[1].strip()
            
            student = query_db('SELECT * FROM students WHERE matric_no = ?', [matric_no], one=True)
            if student and check_password_hash(student['pin_hash'], pin):
                session['logged_in_user'] = matric_no
                session['awaiting_login'] = False
                pending_action = session.get('pending_action')
                session.pop('pending_action', None)
                
                # Execute the database query they originally asked for
                data_response = handle_database_action(pending_action, matric_no)
                return f"Login successful, {student['full_name']}. {data_response}"
            else:
                return "Authentication failed. Invalid Matric Number or PIN. Please try again or ask another question."
        else:
            return "Invalid format. Please provide your details exactly like this: MatricNumber, PIN (e.g., 22/03CYB059, 1234)"

    # --- NORMAL AI PREDICTION (via shared predictor module) ---
    tag, confidence = predict_intent(user_text)

    if tag and confidence > CONFIDENCE_THRESHOLD:
        # Check if this tag requires database authentication
        if tag in ["check_fees", "check_results", "check_accommodation", "check_courses", "check_payment_history"]:
            if 'logged_in_user' in session:
                return handle_database_action(tag, session['logged_in_user'])
            else:
                session['awaiting_login'] = True
                session['pending_action'] = tag
                return "🔒 This request requires authentication. Please enter your Matric Number and PIN separated by a comma (e.g., 22/03CYB059, 1234)."

        # Otherwise, return a standard text response
        response = get_text_response(tag)
        if response:
            return response

    return "I am not entirely sure about that. Could you rephrase your question or contact the administrative office."

# 5. Web Routes
@app.route("/")
def home():
    # Clear session on page load so they have to log in again if they refresh
    session.clear() 
    return render_template("index.html")

@app.route("/logout", methods=["POST"])
def logout():
    student_name = None
    if 'logged_in_user' in session:
        student = query_db('SELECT full_name FROM students WHERE matric_no = ?', [session['logged_in_user']], one=True)
        if student:
            student_name = student['full_name']
    session.clear()
    message = f"Goodbye, {student_name}! You have been logged out successfully." if student_name else "You have been logged out."
    return jsonify({"reply": message})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # Allow students to log out by typing a command mid-conversation
    if user_message and user_message.strip().lower() in ["logout", "log out", "sign out", "signout"]:
        student_name = None
        if 'logged_in_user' in session:
            student = query_db('SELECT full_name FROM students WHERE matric_no = ?', [session['logged_in_user']], one=True)
            if student:
                student_name = student['full_name']
        session.clear()
        message = f"Goodbye, {student_name}! You have been logged out successfully." if student_name else "You are not currently logged in."
        return jsonify({"reply": message})

    bot_reply = get_bot_response(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)