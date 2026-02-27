import json
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

def evaluate_model():
    print("Loading AI Model and Held-Out Test Data (unseen phrases)...")
    
    # 1. Load the Model and Tokenizer
    model = load_model("advanced_chatbot_model.h5")
    
    with open("tokenizer.pickle", "rb") as handle:
        saved_data = pickle.load(handle)
        tokenizer = saved_data['tokenizer']
        classes = saved_data['classes']
        max_length = saved_data['max_length']

    # 2. Load the Held-Out Test Data (from test_intents.json)
    # IMPORTANT: We load from test_intents.json, NOT intents.json.
    # intents.json contains training data - testing on it only measures memorization.
    # test_intents.json contains fresh, unseen phrases the model was never trained on,
    # so these results reflect real-world generalization performance.
    with open("test_intents.json") as file:
        data = json.load(file)

    y_true = []
    x_texts = []

    for intent in data['intents']:
        # Support both 'test_patterns' and 'patterns' keys for flexibility
        patterns = intent.get('test_patterns', intent.get('patterns', []))
        for pattern in patterns:
            x_texts.append(pattern)
            y_true.append(intent['tag'])

    # 3. Process the Text the same way the app does
    seq = tokenizer.texts_to_sequences(x_texts)
    padded = pad_sequences(seq, padding='post', maxlen=max_length)

    # 4. Make Predictions
    print(f"Testing the model on {len(x_texts)} different phrases...")
    predictions = model.predict(padded, verbose=0)
    
    y_pred = []
    for pred in predictions:
        tag_idx = np.argmax(pred)
        y_pred.append(classes[tag_idx])

    # 5. Calculate Metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)

    print("\n" + "="*50)
    print("🏆 FINAL MODEL EVALUATION METRICS 🏆")
    print("="*50)
    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print("="*50)

    # 6. Generate and Save Visual Graphs for Documentation
    print("\nGenerating thesis-ready graphs...")

    # Chart 1: Overall Metrics Bar Chart
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    metrics_values = [accuracy, precision, recall, f1]

    plt.figure(figsize=(8, 5))
    sns.barplot(x=metrics_names, y=metrics_values, palette="viridis")
    plt.ylim(0, 1.1)
    plt.title('Chatbot Performance Metrics (Held-Out Test Set)', fontsize=14, fontweight='bold')
    plt.ylabel('Score (0.0 to 1.0)', fontsize=12)
    for i, v in enumerate(metrics_values):
        plt.text(i, v + 0.02, f"{v*100:.1f}%", ha='center', fontweight='bold')
    plt.savefig('performance_metrics_chart.png', bbox_inches='tight')
    plt.close()

    # Chart 2: Confusion Matrix
    # We filter unique classes that actually appeared in the test to keep the matrix clean
    unique_labels = sorted(list(set(y_true)))
    cm = confusion_matrix(y_true, y_pred, labels=unique_labels)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=unique_labels, yticklabels=unique_labels)
    plt.title('Intent Classification Confusion Matrix', fontsize=16, fontweight='bold')
    plt.xlabel('Predicted Intent', fontsize=12)
    plt.ylabel('Actual Intent', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', bbox_inches='tight')
    plt.close()

    print("✅ Evaluation complete! Two graph images have been saved in your folder:")
    print("   1. performance_metrics_chart.png")
    print("   2. confusion_matrix.png")

if __name__ == "__main__":
    evaluate_model()