"""
predictor.py — Shared AI Prediction Module
-------------------------------------------
This module centralises all model loading and prediction logic.
Both app.py (Flask web interface) and chatbot.py (terminal interface)
import from here. Any bug fix or improvement only needs to be made once.
"""

import json
import random
import pickle
import numpy as np
import re
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# --------------------------------------------------------
# 1. Load the Advanced AI Brain (runs once on import)
# --------------------------------------------------------
print("Loading Advanced AI Model with Attention Mechanism...")
model = load_model("advanced_chatbot_model.h5")

with open("tokenizer.pickle", "rb") as handle:
    saved_data = pickle.load(handle)
    tokenizer = saved_data['tokenizer']
    classes = saved_data['classes']
    max_length = saved_data['max_length']

with open("intents.json") as file:
    intents_data = json.load(file)

print("✅ AI Model loaded successfully.\n")

# --------------------------------------------------------
# 2. Input Sanitization
# --------------------------------------------------------
def sanitize_input(text):
    """
    Strips characters that are not needed for NLP while preserving:
    - Letters and numbers
    - Common punctuation (? . ,)
    - Forward slash for matric number format e.g. 22/03CYB059
    - Apostrophes for contractions
    """
    return re.sub(r'[^a-zA-Z0-9\s\?\.,\'/]', '', text)

# --------------------------------------------------------
# 3. Core Prediction Function
# --------------------------------------------------------
def predict_intent(text):
    """
    Takes a raw user input string and returns a (tag, confidence) tuple.
    Returns (None, 0.0) if the input is empty after sanitization.
    """
    clean_text = sanitize_input(text)
    if not clean_text.strip():
        return None, 0.0

    seq = tokenizer.texts_to_sequences([clean_text])
    padded = pad_sequences(seq, padding='post', maxlen=max_length)

    pred = model.predict(padded, verbose=0)[0]
    tag_idx = np.argmax(pred)
    confidence = float(pred[tag_idx])
    tag = classes[tag_idx]

    return tag, confidence

# --------------------------------------------------------
# 4. Standard Text Response (for non-database intents)
# --------------------------------------------------------
def get_text_response(tag):
    """
    Looks up a tag in intents.json and returns a random response.
    Returns None if the tag is not found.
    """
    for intent in intents_data['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return None

# --------------------------------------------------------
# 5. Confidence Threshold
# --------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.45