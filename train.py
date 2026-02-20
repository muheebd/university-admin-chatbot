import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout, Bidirectional, Attention, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Download required NLTK data
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# --------------------------------------------------------
# 1. Data Collection and Preprocessing
# --------------------------------------------------------
print("Loading and Preprocessing Data...")
with open("intents.json") as file:
    data = json.load(file)

training_sentences = []
training_labels = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])

classes = sorted(list(set(training_labels)))
num_classes = len(classes)

# Tokenization and Embedding Prep
vocab_size = 2000
embedding_dim = 64

tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
tokenizer.fit_on_texts(training_sentences)
sequences = tokenizer.texts_to_sequences(training_sentences)

max_length = max([len(seq) for seq in sequences])
padded_sequences = pad_sequences(sequences, padding='post', maxlen=max_length)

# Encode Labels
training_labels_encoded = np.array([classes.index(label) for label in training_labels])

# Save Tokenizer Data
with open("tokenizer.pickle", "wb") as handle:
    pickle.dump({'tokenizer': tokenizer, 'classes': classes, 'max_length': max_length}, handle, protocol=pickle.HIGHEST_PROTOCOL)

# --------------------------------------------------------
# 2. Model Development (Seq2Seq Architecture with Attention)
# --------------------------------------------------------
print("Building the LSTM + Attention Architecture...")

# Input Layer
inputs = Input(shape=(max_length,))

# Embedding Layer
# This satisfies the requirement for numerical representation using embedding techniques
x = Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length)(inputs)

# LSTM Encoder (Bidirectional to capture context from both directions)
lstm_out = Bidirectional(LSTM(64, return_sequences=True))(x)

# Attention Mechanism
# This allows the model to focus selectively on relevant portions of the input sequence
attention_out = Attention()([lstm_out, lstm_out])

# Pooling layer to flatten the data for the Dense layers
pooled_output = GlobalAveragePooling1D()(attention_out)

# Dense / Softmax Layer for Intent Recognition
x = Dense(64, activation='relu')(pooled_output)
x = Dropout(0.5)(x)
outputs = Dense(num_classes, activation='softmax')(x)

# Compile Model
model = Model(inputs=inputs, outputs=outputs)
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# --------------------------------------------------------
# 3. Model Training and Evaluation
# --------------------------------------------------------
print("Training the Deep Learning Model...")
# Training on the preprocessed dataset using supervised learning
history = model.fit(padded_sequences, training_labels_encoded, epochs=200, batch_size=8, verbose=1)

# Save the advanced model
model.save("advanced_chatbot_model.h5")
print("\n✅ Training complete! Architecture with Attention Mechanism successfully saved.")