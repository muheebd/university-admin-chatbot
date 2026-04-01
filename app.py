import json
import random
import pickle
import numpy as np
import re
import sqlite3
import os
from werkzeug.security import check_password_hash
from flask import Flask, render_template, request, jsonify, session
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
secret_key = os.environ.get("FLASK_SECRET_KEY")
if not secret_key:
    raise RuntimeError("FLASK_SECRET_KEY not set in .env file.")
app.secret_key = secret_key

print("Loading Advanced AI Model with Attention Mechanism...")
model = load_model("advanced_chatbot_model.h5")

with open("tokenizer.pickle", "rb") as handle:
    saved_data = pickle.load(handle)
    tokenizer  = saved_data['tokenizer']
    classes    = saved_data['classes']
    max_length = saved_data['max_length']

with open("intents.json") as file:
    data = json.load(file)

CONFIDENCE_THRESHOLD = 0.45
CURRENT_SESSION      = "2025/2026"

print("✅ AI Model loaded successfully.")


def sanitize_input(text):
    return re.sub(r"[^a-zA-Z0-9\s\?\.,\'/]", '', text)


def query_db(query, args=(), one=False):
    conn = sqlite3.connect('university.db')
    conn.row_factory = sqlite3.Row
    cur  = conn.cursor()
    cur.execute(query, args)
    rv   = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def semester_from_input(text):
    """Return normalised semester string or None."""
    t = text.strip().lower()
    if t in ('1', '1st', '1st semester', 'first', 'first semester'):
        return '1st Semester'
    if t in ('2', '2nd', '2nd semester', 'second', 'second semester'):
        return '2nd Semester'
    return None


def get_standing(cgpa):
    if   cgpa >= 4.5: return "First Class 🏆"
    elif cgpa >= 3.5: return "Second Class Upper"
    elif cgpa >= 2.4: return "Second Class Lower"
    elif cgpa >= 1.5: return "Third Class"
    else:             return "Academic Probation ⚠️"


def format_results_html(matric_no, sess, sem):
    """Return an HTML table of course grades for one semester."""
    grades = query_db('''
        SELECT * FROM course_grades
        WHERE matric_no = ? AND session = ? AND semester = ?
        ORDER BY course_code
    ''', [matric_no, sess, sem])

    result_row = query_db('''
        SELECT gpa, cgpa FROM results
        WHERE matric_no = ? AND session = ? AND semester = ?
    ''', [matric_no, sess, sem], one=True)

    if not grades:
        return f"No results found for {sess} {sem}."

    rows = ""
    for g in grades:
        rows += (f"<tr>"
                 f"<td>{g['course_code']}</td>"
                 f"<td>{g['course_title']}</td>"
                 f"<td style='text-align:center'>{g['units']}</td>"
                 f"<td style='text-align:center'>{g['score']}</td>"
                 f"<td style='text-align:center;font-weight:600'>{g['grade']}</td>"
                 f"<td style='text-align:center'>{g['grade_point']:.1f}</td>"
                 f"</tr>")

    gpa_row = ""
    if result_row:
        standing = get_standing(result_row['cgpa'])
        gpa_row  = (f"<tr style='background:#f0f7f4;font-weight:600'>"
                    f"<td colspan='6' style='padding-top:10px'>"
                    f"Semester GPA: {result_row['gpa']} &nbsp;|&nbsp; "
                    f"Cumulative CGPA: {result_row['cgpa']} ({standing})"
                    f"</td></tr>")

    html = f"""
<div style='font-size:13px'>
  <strong>📋 Results — {sess} {sem}</strong>
  <table style='width:100%;border-collapse:collapse;margin-top:8px;font-size:12px'>
    <thead>
      <tr style='background:#00563b;color:white'>
        <th style='padding:6px 8px;text-align:left'>Code</th>
        <th style='padding:6px 8px;text-align:left'>Course Title</th>
        <th style='padding:6px 4px;text-align:center'>Units</th>
        <th style='padding:6px 4px;text-align:center'>Score</th>
        <th style='padding:6px 4px;text-align:center'>Grade</th>
        <th style='padding:6px 4px;text-align:center'>GP</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      {gpa_row}
    </tbody>
  </table>
</div>"""
    return html


def handle_database_action(action_tag, matric_no):
    if action_tag == "check_fees":
        finance = query_db('SELECT * FROM finances WHERE matric_no = ?', [matric_no], one=True)
        if finance:
            return (f"Your total billed fees are ₦{finance['total_billed']:,.2f}. "
                    f"You have paid ₦{finance['amount_paid']:,.2f}. "
                    f"Your outstanding balance is ₦{finance['balance']:,.2f}. "
                    f"Clearance Status: {finance['clearance_status']}.")
        return "No fee record found. Please visit the Bursary office."

    elif action_tag == "check_results":
        session['awaiting_semester'] = 'results'
        return (f"Which semester results do you want to view for {CURRENT_SESSION}? "
                f"Reply with <strong>1st Semester</strong> or <strong>2nd Semester</strong>.")

    elif action_tag == "check_courses":
        session['awaiting_semester'] = 'courses'
        return (f"Which semester courses do you want to view for {CURRENT_SESSION}? "
                f"Reply with <strong>1st Semester</strong> or <strong>2nd Semester</strong>.")

    elif action_tag == "check_accommodation":
        hostel = query_db('SELECT * FROM accommodation WHERE matric_no = ?', [matric_no], one=True)
        if hostel:
            if hostel['status'] == 'Allocated':
                return (f"Accommodation Status: Allocated ✅. "
                        f"You are assigned to {hostel['hostel_name']}, {hostel['room_number']}.")
            else:
                return ("Accommodation Status: Not Allocated. "
                        "Log into your student portal and apply under Student Services.")
        return "No accommodation record found. Please visit the Student Affairs office."

    elif action_tag == "check_payment_history":
        payment = query_db('''
            SELECT * FROM payments_history WHERE matric_no = ?
            ORDER BY date DESC LIMIT 1
        ''', [matric_no], one=True)
        if payment:
            return (f"Your last transaction was on {payment['date']}. "
                    f"Amount: ₦{payment['amount']:,.2f} for {payment['payment_type']}. "
                    f"Receipt No: {payment['receipt_no']}. Status: {payment['status']}.")

    return "I couldn't find those records. Please visit the admin office."


def get_bot_response(user_text):
    clean_text = sanitize_input(user_text)
    if not clean_text.strip():
        return "Please enter a valid question."

    # ── Logout ──
    if clean_text.lower().strip() in ['logout', 'log out', 'sign out', 'signout']:
        name = ''
        if 'logged_in_user' in session:
            s = query_db('SELECT full_name FROM students WHERE matric_no = ?',
                         [session['logged_in_user']], one=True)
            if s: name = f", {s['full_name']}"
        session.clear()
        return f"Goodbye{name}! You have been logged out successfully."

    # ── Semester selection ──
    if session.get('awaiting_semester'):
        sem = semester_from_input(clean_text)
        if sem:
            mode    = session.pop('awaiting_semester')
            matric  = session.get('logged_in_user')

            if mode == 'results':
                return format_results_html(matric, CURRENT_SESSION, sem)

            elif mode == 'courses':
                courses = query_db('''
                    SELECT * FROM course_registration
                    WHERE matric_no = ? AND session = ? AND semester = ?
                    ORDER BY course_code
                ''', [matric, CURRENT_SESSION, sem])
                if courses:
                    rows = "".join(
                        f"<tr><td>{c['course_code']}</td><td>{c['course_title']}</td>"
                        f"<td style='text-align:center'>{c['units']}</td></tr>"
                        for c in courses
                    )
                    total = sum(c['units'] for c in courses)
                    return f"""
<div style='font-size:13px'>
  <strong>📝 Registered Courses — {CURRENT_SESSION} {sem}</strong>
  <table style='width:100%;border-collapse:collapse;margin-top:8px;font-size:12px'>
    <thead>
      <tr style='background:#00563b;color:white'>
        <th style='padding:6px 8px;text-align:left'>Code</th>
        <th style='padding:6px 8px;text-align:left'>Course Title</th>
        <th style='padding:6px 4px;text-align:center'>Units</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr style='background:#f0f7f4;font-weight:600'>
        <td colspan='2' style='padding-top:8px'>Total Units</td>
        <td style='text-align:center;padding-top:8px'>{total}</td>
      </tr>
    </tbody>
  </table>
</div>"""
                return f"No courses found for {CURRENT_SESSION} {sem}."
        else:
            return "Please reply with <strong>1st Semester</strong> or <strong>2nd Semester</strong>."

    # ── Awaiting login ──
    if session.get('awaiting_login'):
        parts = clean_text.split(',')
        if len(parts) == 2:
            matric_no = parts[0].strip().upper()
            pin       = parts[1].strip()
            student   = query_db('SELECT * FROM students WHERE matric_no = ?', [matric_no], one=True)
            if student and check_password_hash(student['pin_hash'], pin):
                session['logged_in_user'] = matric_no
                session['awaiting_login'] = False
                pending_action = session.pop('pending_action', None)
                data_response  = handle_database_action(pending_action, matric_no)
                return (f"Login successful, {student['full_name']}. "
                        f"[PROFILE: {matric_no} | {student['department']} | Level {student['level']}] "
                        f"{data_response}")
            else:
                return "Authentication failed. Invalid Matric Number or PIN. Please try again."
        else:
            return "Invalid format. Please use: MatricNumber, PIN  (e.g. 22/03CYB059, 1234)"

    # ── AI prediction ──
    seq        = tokenizer.texts_to_sequences([clean_text])
    padded     = pad_sequences(seq, padding='post', maxlen=max_length)
    pred       = model.predict(padded, verbose=0)[0]
    tag_idx    = np.argmax(pred)
    confidence = pred[tag_idx]

    if confidence > CONFIDENCE_THRESHOLD:
        tag = classes[tag_idx]

        if tag in ["check_fees", "check_results", "check_accommodation",
                   "check_courses", "check_payment_history"]:
            if 'logged_in_user' in session:
                return handle_database_action(tag, session['logged_in_user'])
            else:
                session['awaiting_login'] = True
                session['pending_action'] = tag
                return ("🔒 This request requires authentication. "
                        "Please enter your Matric Number and PIN separated by a comma "
                        "(e.g., 22/03CYB059, 1234).")

        for intent in data['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])

    return "I am not entirely sure about that. Could you rephrase your question or contact the administrative office?"


# 6. Web Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chatbot")
def chatbot():
    session.clear()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    bot_reply    = get_bot_response(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)