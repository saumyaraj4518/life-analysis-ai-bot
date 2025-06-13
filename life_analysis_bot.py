
import streamlit as st
import openai
from textblob import TextBlob
import json

# --------- SETUP ---------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --------- INITIALIZE SESSION STATE ---------
if "responses" not in st.session_state:
    st.session_state.responses = []

# --------- INTERVIEW QUESTIONS ---------
questions = [
    "Tell me about your daily routine.",
    "What are your short-term and long-term goals?",
    "How do you usually handle stress?",
    "Describe your recent mood in one or two sentences.",
    "How do you feel about your social life?",
    "What motivates you the most in life?"
]

# --------- FUNCTION: Analyze Text ---------
def analyze_response(text):
    sentiment = TextBlob(text).sentiment
    return {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity
    }

# --------- FUNCTION: OpenAI Personality Summary ---------
def generate_personality_summary(responses):
    joined_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, responses)])
    prompt = f"""
You are an AI life coach. Based on the following responses, give a personality analysis and life insight report:

{joined_text}

Give a friendly, supportive summary:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful, wise life coach."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

# --------- STREAMLIT UI ---------
st.title("🧠 Life Analysis AI Bot")
st.write("Answer the following questions to get a personality and life analysis.")

for i, question in enumerate(questions):
    if len(st.session_state.responses) > i:
        st.text_area(f"{question}", value=st.session_state.responses[i], key=f"q{i}", disabled=True)
    else:
        answer = st.text_area(f"{question}", key=f"q{i}")
        if answer:
            st.session_state.responses.append(answer)
            st.experimental_rerun()

# --------- ANALYSIS ---------
if len(st.session_state.responses) == len(questions):
    if st.button("🔍 Analyze My Life"):
        st.subheader("📊 Sentiment Analysis:")
        for i, answer in enumerate(st.session_state.responses):
            result = analyze_response(answer)
            st.write(f"**Q{i+1}:** {questions[i]}")
            st.write(f"Polarity: {result['polarity']:.2f}, Subjectivity: {result['subjectivity']:.2f}")
            st.markdown("---")

        st.subheader("🧬 Personality & Life Summary:")
        summary = generate_personality_summary(st.session_state.responses)
        st.write(summary)

        # Optional: Save to file
        with open("life_analysis_result.json", "w") as f:
            json.dump({"questions": questions, "responses": st.session_state.responses, "summary": summary}, f, indent=4)
        st.success("Results saved to 'life_analysis_result.json'")
