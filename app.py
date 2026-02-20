import json
import random
import pickle
import numpy as np
import re
import sqlite3
from werkzeug.security import check_password_hash
from flask import Flask, render_template, request, jsonify, session
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)
# A secret key is required for Flask sessions to keep track of logged-in students
app.secret_key = "alhikmah_cyber_security_key"

# 1. Load the Advanced AI Brain
print("Loading Advanced AI Model...")
model = load_model("advanced_chatbot_model.h5")

with open("tokenizer.pickle", "rb") as handle:
    saved_data = pickle.load(handle)
    tokenizer = saved_data['tokenizer']
    classes = saved_data['classes']
    max_length = saved_data['max_length']

with open("intents.json") as file:
    data = json.load(file)

def sanitize_input(text):
    # Added the forward slash '/' to the allowed characters for Matric Numbers!
    return re.sub(r'[^a-zA-Z0-9\s\?\.,\'/]', '', text)

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
            return f"Your total billed fees are ₦{finance['total_billed']:,.2f}. You have paid ₦{finance['amount_paid']:,.2f}. Your outstanding balance is ₦{finance['balance']:,.2f}. Clearance Status: {finance['clearance_status']}."
    
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
    clean_text = sanitize_input(user_text)
    if not clean_text.strip():
        return "Please enter a valid question."

    # --- SESSION MANAGEMENT: Check if the bot is currently waiting for login details ---
    if session.get('awaiting_login'):
        # Expecting format: MatricNo, PIN (e.g., 22/03CYB059, 1234)
        parts = clean_text.split(',')
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

    # --- NORMAL AI PREDICTION ---
    seq = tokenizer.texts_to_sequences([clean_text])
    padded = pad_sequences(seq, padding='post', maxlen=max_length)
    
    pred = model.predict(padded, verbose=0)[0]
    tag_idx = np.argmax(pred)
    confidence = pred[tag_idx]
    
    if confidence > 0.60:
        tag = classes[tag_idx]
        
        # Check if this tag requires database authentication
        if tag in ["check_fees", "check_results", "check_accommodation", "check_courses", "check_payment_history"]:
            if 'logged_in_user' in session:
                return handle_database_action(tag, session['logged_in_user'])
            else:
                session['awaiting_login'] = True
                session['pending_action'] = tag
                return "🔒 This request requires authentication. Please enter your Matric Number and PIN separated by a comma (e.g., 22/03CYB059, 1234)."
        
        # Otherwise, return a standard text response
        for intent in data['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
    
    return "I am not entirely sure about that. Could you rephrase your question or contact the administrative office?"

# 5. Web Routes
@app.route("/")
def home():
    # Clear session on page load so they have to log in again if they refresh
    session.clear() 
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    bot_reply = get_bot_response(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)