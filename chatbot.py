"""
chatbot.py — Terminal Interface
--------------------------------
Runs the Al-Hikmah Admin Bot as a command-line chatbot.
All AI logic is handled by predictor.py.
"""

from predictor import predict_intent, get_text_response, CONFIDENCE_THRESHOLD

def chat_response(text):
    """Returns a bot response string for a given user input."""
    if not text.strip():
        return "Please enter a valid question."

    tag, confidence = predict_intent(text)

    if tag is None:
        return "Please enter a valid question."

    if confidence > CONFIDENCE_THRESHOLD:
        response = get_text_response(tag)
        if response:
            return response

    return "I am not entirely sure about that. Could you rephrase your question or contact the administrative office?"

# --------------------------------------------------------
# Terminal Chat Loop
# --------------------------------------------------------
print("=======================================================")
print("🎓 Advanced Al-Hikmah Admin Bot (Attention-Enabled) Ready!")
print("=======================================================")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("Student: ")
    if user_input.lower() in ["quit", "exit", "bye"]:
        print("Bot: Goodbye! Have a great day.")
        break

    response = chat_response(user_input)
    print("Bot:", response, "\n")