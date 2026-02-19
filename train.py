import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Download required NLTK data (runs only if not already downloaded)
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# 1. Load Intents
with open("intents.json") as file:
    data = json.load(file)

training_sentences = []
training_labels = []

# 2. Extract Data
for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])

# 3. Create a SORTED list of unique classes (Crucial for avoiding mapping bugs)
classes = sorted(list(set(training_labels)))
num_classes = len(classes)

# 4. Tokenization & Padding
tokenizer = Tokenizer(num_words=2000, oov_token="<OOV>")
tokenizer.fit_on_texts(training_sentences)
sequences = tokenizer.texts_to_sequences(training_sentences)

# Find the longest sentence to set a dynamic max length
max_length = max([len(seq) for seq in sequences]) 
padded_sequences = pad_sequences(sequences, padding='post', maxlen=max_length)

# Encode Labels dynamically based on the sorted classes
training_labels_encoded = np.array([classes.index(label) for label in training_labels])

# 5. Save Tokenizer, Classes, and Max Length for the Chatbot script
with open("tokenizer.pickle", "wb") as handle:
    pickle.dump({'tokenizer': tokenizer, 'classes': classes, 'max_length': max_length}, handle, protocol=pickle.HIGHEST_PROTOCOL)

# 6. Build the LSTM Model
model = Sequential()
model.add(Embedding(input_dim=2000, output_dim=16, input_length=max_length))
model.add(LSTM(32, return_sequences=False))
model.add(Dropout(0.5))
model.add(Dense(32, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# 7. Train the Model
print("Training the Deep Learning Model...")
history = model.fit(padded_sequences, training_labels_encoded, epochs=200, verbose=1)

# 8. Save the Model
model.save("chatbot_model.h5")
print("\n✅ Training complete! Model, Tokenizer, and Classes successfully saved.")