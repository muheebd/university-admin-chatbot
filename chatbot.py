import json
import random
import pickle
import numpy as np
import re
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 1. Load the Advanced AI Brain
print("Loading Advanced AI Model with Attention Mechanism...")
model = load_model("advanced_chatbot_model.h5")

# 2. Load Tokenizer and Classes
with open("tokenizer.pickle", "rb") as handle:
    saved_data = pickle.load(handle)
    tokenizer = saved_data['tokenizer']
    classes = saved_data['classes']
    max_length = saved_data['max_length']

# 3. Load Intents JSON
with open("intents.json") as file:
    data = json.load(file)

# 4. Input Sanitization Filter
def sanitize_input(text):
    return re.sub(r'[^a-zA-Z0-9\s\?\.,\']', '', text)

# 5. Deep Learning Prediction Logic
def chat_response(text):
    clean_text = sanitize_input(text)
    
    if not clean_text.strip():
        return "Please enter a valid question."

    # Convert words to numbers
    seq = tokenizer.texts_to_sequences([clean_text])
    padded = pad_sequences(seq, padding='post', maxlen=max_length)
    
    # Predict using the attention model
    pred = model.predict(padded, verbose=0)[0]
    tag_idx = np.argmax(pred)
    confidence = pred[tag_idx]
    
    # Only answer if more than 60% confident
    if confidence > 0.60:
        tag = classes[tag_idx]
        for intent in data['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
    else:
        return "I am not entirely sure about that. Could you rephrase your question or contact the administrative office?"

# 6. The Chat Loop
print("\n=======================================================")
print("🎓 Advanced Al-Hikmah Admin Bot (Attention-Enabled) Ready!")
print("=======================================================")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("Student: ")
    if user_input.lower() == "quit":
        print("Bot: Goodbye! Have a great day.")
        break
    
    response = chat_response(user_input)
    print("Bot:", response, "\n")