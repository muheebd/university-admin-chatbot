import json
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support
)


def evaluate_model():
    print("Loading AI Model and Held-Out Test Data (unseen phrases)...")

    # 1. Load the Model and Tokenizer
    model = load_model("advanced_chatbot_model.h5")

    with open("tokenizer.pickle", "rb") as handle:
        saved_data = pickle.load(handle)
        tokenizer = saved_data['tokenizer']
        classes = saved_data['classes']
        max_length = saved_data['max_length']

    # 2. Load Held-Out Test Data
    # IMPORTANT: We load from test_intents.json, NOT intents.json.
    # intents.json contains training data - testing on it only measures memorization.
    # test_intents.json contains fresh unseen phrases, giving honest generalization scores.
    with open("test_intents.json") as file:
        data = json.load(file)

    x_texts = []
    y_true = []

    for intent in data['intents']:
        patterns = intent.get('test_patterns', intent.get('patterns', []))
        for pattern in patterns:
            x_texts.append(pattern)
            y_true.append(intent['tag'])

    # 3. Process Text
    seq = tokenizer.texts_to_sequences(x_texts)
    padded = pad_sequences(seq, padding='post', maxlen=max_length)

    # 4. Make Predictions
    print(f"Testing the model on {len(x_texts)} unseen phrases across {len(data['intents'])} intents...\n")
    predictions = model.predict(padded, verbose=0)

    y_pred = []
    for pred in predictions:
        tag_idx = np.argmax(pred)
        y_pred.append(classes[tag_idx])

    # 5. Overall Metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )

    print("=" * 55)
    print("        FINAL MODEL EVALUATION METRICS")
    print("=" * 55)
    print(f"  Accuracy:  {accuracy * 100:.2f}%")
    print(f"  Precision: {precision * 100:.2f}%")
    print(f"  Recall:    {recall * 100:.2f}%")
    print(f"  F1-Score:  {f1 * 100:.2f}%")
    print("=" * 55)

    # 6. Per-Intent Breakdown
    print("\nPER-INTENT CLASSIFICATION REPORT:")
    print("-" * 55)
    print(classification_report(y_true, y_pred, zero_division=0))

    # 7. Show any misclassified phrases
    print("MISCLASSIFIED PHRASES:")
    print("-" * 55)
    misses = [(x_texts[i], y_true[i], y_pred[i])
              for i in range(len(y_true)) if y_true[i] != y_pred[i]]
    if misses:
        for phrase, actual, predicted in misses:
            print(f"  Phrase:    \"{phrase}\"")
            print(f"  Expected:  {actual}")
            print(f"  Got:       {predicted}")
            print()
    else:
        print("  None - model correctly classified all test phrases!\n")

    # 8. Generate Graphs
    print("Generating thesis-ready graphs...")

    # Graph 1: Overall Metrics Bar Chart
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    metrics_values = [accuracy, precision, recall, f1]

    plt.figure(figsize=(8, 5))
    sns.barplot(x=metrics_names, y=metrics_values, palette="viridis",
                hue=metrics_names, legend=False)
    plt.ylim(0, 1.15)
    plt.title('Chatbot Performance Metrics (Held-Out Test Set)',
              fontsize=14, fontweight='bold')
    plt.ylabel('Score (0.0 to 1.0)', fontsize=12)
    for i, v in enumerate(metrics_values):
        plt.text(i, v + 0.03, f"{v * 100:.1f}%", ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig('performance_metrics_chart.png', bbox_inches='tight', dpi=150)
    plt.close()
    print("  Saved: performance_metrics_chart.png")

    # Graph 2: Confusion Matrix
    unique_labels = sorted(list(set(y_true)))
    cm = confusion_matrix(y_true, y_pred, labels=unique_labels)

    plt.figure(figsize=(14, 11))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=unique_labels, yticklabels=unique_labels
    )
    plt.title('Intent Classification Confusion Matrix',
              fontsize=16, fontweight='bold')
    plt.xlabel('Predicted Intent', fontsize=12)
    plt.ylabel('Actual Intent', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', bbox_inches='tight', dpi=150)
    plt.close()
    print("  Saved: confusion_matrix.png")

    # Graph 3: Per-Intent F1 Score Bar Chart
    per_intent_precision, per_intent_recall, per_intent_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=unique_labels, zero_division=0
    )

    plt.figure(figsize=(14, 6))
    x_pos = range(len(unique_labels))
    bars = plt.bar(x_pos, per_intent_f1, color='steelblue', edgecolor='white')
    plt.xticks(x_pos, unique_labels, rotation=45, ha='right', fontsize=9)
    plt.ylim(0, 1.15)
    plt.title('F1-Score Per Intent (Held-Out Test Set)',
              fontsize=14, fontweight='bold')
    plt.ylabel('F1-Score', fontsize=12)
    for bar, val in zip(bars, per_intent_f1):
        plt.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.03,
                 f"{val:.2f}", ha='center', fontsize=8, fontweight='bold')
    plt.tight_layout()
    plt.savefig('per_intent_f1_chart.png', bbox_inches='tight', dpi=150)
    plt.close()
    print("  Saved: per_intent_f1_chart.png")

    print("\nEvaluation complete! Three graph images saved in your project folder.")


if __name__ == "__main__":
    evaluate_model()