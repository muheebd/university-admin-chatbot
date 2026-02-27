# 🎓 Al-Hikmah University Admin Chatbot

An intelligent deep learning-based chatbot for university administrative support, built as a final year project for Al-Hikmah University. The system uses a Bidirectional LSTM with an Attention Mechanism to classify student intents and provide real-time responses to administrative queries — including personalised information like fee balances, results, accommodation, and course registration retrieved securely from a database.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [How to Run](#how-to-run)
- [Demo Login Credentials](#demo-login-credentials)
- [How the Chatbot Works](#how-the-chatbot-works)
- [Evaluation](#evaluation)
- [File Descriptions](#file-descriptions)

---

## ✨ Features

- Natural language intent classification using Bidirectional LSTM + Attention
- Handles 15 intent categories covering common university administrative queries
- Secure student authentication (Matric Number + PIN) for personal data access
- Live database queries for fee balances, results, accommodation, and course registration
- Web interface built with Flask
- Terminal interface for quick local testing
- Evaluation script that generates performance metrics and graphs

---

## 📁 Project Structure

```
├── app.py                  # Flask web application (main entry point)
├── chatbot.py              # Terminal-based chat interface
├── predictor.py            # Shared AI model loading and prediction logic
├── train.py                # Model training script
├── evaluate.py             # Model evaluation and graph generation
├── setup_database.py       # Database creation and mock data population
├── intents.json            # Training data (patterns and responses)
├── test_intents.json       # Held-out test data for honest evaluation
├── advanced_chatbot_model.h5   # Trained deep learning model (generated)
├── tokenizer.pickle            # Saved tokenizer and metadata (generated)
├── university.db               # SQLite student database (generated)
├── .env                    # Secret keys — never share or commit this
├── .gitignore              # Prevents sensitive files from being committed
└── templates/
    └── index.html          # Web chat interface
```

---

## 🛠️ Technologies Used

| Technology           | Purpose                                |
| -------------------- | -------------------------------------- |
| Python 3.10+         | Core programming language              |
| TensorFlow / Keras   | Deep learning model (LSTM + Attention) |
| Flask                | Web application framework              |
| SQLite               | Student records database               |
| NLTK                 | Natural language preprocessing         |
| scikit-learn         | Evaluation metrics                     |
| Matplotlib / Seaborn | Performance graphs                     |
| Werkzeug             | Secure password hashing                |
| python-dotenv        | Environment variable management        |

---

## ⚙️ Setup Instructions

### 1. Clone or download the project

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install all dependencies

```bash
pip install tensorflow flask nltk scikit-learn matplotlib seaborn werkzeug python-dotenv
```

### 4. Set up your environment variables

Create a `.env` file in the root of the project (or use the one provided):

```
FLASK_SECRET_KEY=your_random_secret_key_here
```

To generate a strong key, run:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Set up the database

This creates `university.db` with 151 student records across all Al-Hikmah faculties:

```bash
python setup_database.py
```

### 6. Train the model

This trains the LSTM model on `intents.json` and saves `advanced_chatbot_model.h5` and `tokenizer.pickle`:

```bash
python train.py
```

> **Note:** Training runs up to 200 epochs but EarlyStopping will halt it automatically when the model converges. A `training_history.png` graph is saved after training completes.

---

## ▶️ How to Run

### Web Interface (recommended)

```bash
python app.py
```

Then open your browser and go to: **http://127.0.0.1:5000**

### Terminal Interface

```bash
python chatbot.py
```

Type your question at the `Student:` prompt. Type `quit` to exit.

---

## 🔐 Demo Login Credentials

For intents that require personal data (fees, results, accommodation, courses), the bot will prompt for authentication.

Enter credentials in this exact format:

```
MatricNumber, PIN
```

**Master demo account:**

| Field         | Value                                   |
| ------------- | --------------------------------------- |
| Matric Number | `22/03CYB059`                           |
| PIN           | `1234`                                  |
| Name          | Lawal, Muheebdeen Ayodeji               |
| Programme     | B.Sc. (Hons) Cyber Security — 400 Level |

**Example input when prompted:**

```
22/03CYB059, 1234
```

> All 151 mock students in the database also use PIN `1234` for demo purposes.

---

## 🤖 How the Chatbot Works

1. The student types a message in the chat interface.
2. The message is sanitised to remove invalid characters.
3. The text is tokenized and padded to match the model's input format.
4. The trained Bidirectional LSTM + Attention model predicts the intent.
5. If confidence is above 60%, the intent tag is identified.
6. **For general intents** (greetings, admissions, fees info, etc.) — a text response is returned directly from `intents.json`.
7. **For personal data intents** (check_fees, check_results, etc.) — the bot requests authentication, then queries the database and returns the student's specific information.

---

## 📊 Evaluation

To evaluate the model on held-out test data (phrases the model was never trained on):

```bash
python evaluate.py
```

This generates two files:

- `performance_metrics_chart.png` — Bar chart of Accuracy, Precision, Recall, and F1-Score
- `confusion_matrix.png` — Heatmap showing predicted vs actual intents

> **Important:** Evaluation uses `test_intents.json`, not `intents.json`. This ensures the reported metrics reflect real generalisation performance, not just memorisation of training data.

---

## 📄 File Descriptions

| File                | Description                                                                                                                                                      |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app.py`            | Flask web server. Handles routing, session management, student authentication, and database queries. Imports AI logic from `predictor.py`.                       |
| `chatbot.py`        | Lightweight terminal interface for testing the bot locally without starting the web server.                                                                      |
| `predictor.py`      | Shared module that loads the model, tokenizer, and intents once. Exposes `predict_intent()` and `get_text_response()` for use by both `app.py` and `chatbot.py`. |
| `train.py`          | Builds and trains the Bidirectional LSTM + Attention model. Includes EarlyStopping and ModelCheckpoint callbacks. Saves the best model automatically.            |
| `evaluate.py`       | Loads the trained model and runs it against `test_intents.json` to produce honest performance metrics and graphs.                                                |
| `setup_database.py` | Creates the SQLite database with six tables and populates it with 151 student records across all 10 Al-Hikmah faculties.                                         |
| `intents.json`      | Training data containing 297 patterns across 15 intent categories covering both general queries and personalised data requests.                                  |
| `test_intents.json` | Held-out test dataset with 75 unseen phrases (5 per intent) used exclusively by `evaluate.py`. Never used during training.                                       |

---

## 👨‍💻 Author

**Lawal, Muheebdeen Ayodeji**
B.Sc. (Hons) Cyber Security — 400 Level
Faculty of Computing, Engineering and Technology
Al-Hikmah University, Ilorin, Kwara State, Nigeria
