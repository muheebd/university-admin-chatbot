import json
import random
import pickle
import numpy as np
import re
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 1. Load the Trained Model
print("Loading model...")
model = load_model("chatbot_model.h5")

# 2. Load Tokenizer, Classes, and Max Length
with open("tokenizer.pickle", "rb") as handle:
    saved_data = pickle.load(handle)
    tokenizer = saved_data['tokenizer']
    classes = saved_data['classes']
    max_length = saved_data['max_length']

# 3. Load Intents JSON for the text responses
with open("intents.json") as file:
    data = json.load(file)

# --------------------------------------------------------
# 🛡️ CYBER SECURITY FEATURE: Input Sanitization
# Prevents script injection or basic terminal-breaking inputs
# --------------------------------------------------------
def sanitize_input(text):
    # Removes special characters, keeping only words and basic punctuation
    clean_text = re.sub(r'[^a-zA-Z0-9\s\?\.,\']', '', text)
    return clean_text

# --------------------------------------------------------
# 🧠 DEEP LEARNING LOGIC: Predict with Confidence Score
# --------------------------------------------------------
def chat_response(text):
    # Sanitize user input first
    clean_text = sanitize_input(text)
    
    if not clean_text.strip():
        return "Please enter a valid question."

    # Process text for the LSTM model
    seq = tokenizer.texts_to_sequences([clean_text])
    padded = pad_sequences(seq, padding='post', maxlen=max_length)
    
    # Predict probabilities
    pred = model.predict(padded, verbose=0)[0]
    
    # Get highest probability and its corresponding class index
    tag_idx = np.argmax(pred)
    confidence = pred[tag_idx]
    
    # Confidence Threshold (60%)
    if confidence > 0.60:
        tag = classes[tag_idx]
        for intent in data['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
    else:
        return "I am not entirely sure about that. Could you rephrase your question or contact the administrative office?"

# 4. The Chat Loop
print("\n=======================================================")
print("🛡️ Al-Hikmah University Secure Administrative Bot Ready!")
print("=======================================================")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("Student: ")
    if user_input.lower() == "quit":
        print("Bot: Goodbye! Have a great day.")
        break
    
    response = chat_response(user_input)
    print("Bot:", response, "\n")