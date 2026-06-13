import os
import random
import tempfile

import matplotlib.pyplot as plt
import speech_recognition as sr
import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Daily topics
topics = [
    "Some people believe that technology has made life easier, while others think it has made life more complicated. Discuss both views.",
    "Should governments invest more in public transport rather than in roads for private vehicles?",
    "Do you agree or disagree: Social media has a negative impact on face-to-face communication?",
    "The use of plastic should be banned. Discuss the advantages and disadvantages."
]


def get_daily_topic():
    return random.choice(topics)


def is_topic_related(essay, topic):
    if not essay.strip():
        return False

    essay_keywords = set(essay.lower().split()[:20])
    topic_keywords = set(topic.lower().split()[:20])

    similarity = len(
        essay_keywords.intersection(topic_keywords)
    ) / max(len(topic_keywords), 1)

    return similarity > 0.3


@st.cache_data(show_spinner=False)
def get_feedback(essay, level):
    system_prompt = f"""
You are an expert IELTS, TOEFL, and DET writing examiner.

The student's level is: {level}

Provide feedback in the following format:

🔴 Grammar Mistakes:
- Mention mistakes and corrections.

🟡 Cohesion & Flow:
- Suggest improvements in sentence flow and organization.

🟢 Vocabulary Suggestions:
- Suggest stronger vocabulary and better word choices.

📌 Final Summary:
- Bullet point summary of major improvements needed.

Be concise but helpful.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": essay}
            ],
            temperature=0.5,
            max_completion_tokens=1200
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error while generating feedback:\n\n{str(e)}"


def analyze_feedback(feedback):
    sections = {
        "Grammar": feedback.count("Grammar"),
        "Cohesion": feedback.count("Cohesion"),
        "Vocabulary": feedback.count("Vocabulary"),
        "Summary": feedback.count("Summary")
    }

    return sections


def speech_to_text(audio_file):
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(audio)

    except Exception as e:
        return f"Speech recognition error: {e}"


def app():
    st.set_page_config(
        page_title="EssayElevate",
        page_icon="✍️",
        layout="wide"
    )

    st.title("✍️ EssayElevate - Writing Assistant for IELTS, DET, TOEFL")

    st.header("📅 Choose Your Study Plan")

    plans = ["30 Days Plan", "45 Days Plan", "60 Days Plan"]

    cols = st.columns(3)

    for i, plan in enumerate(plans):
        with cols[i]:
            st.subheader(plan)

            if st.button(f"Select {plan}", key=plan):
                st.session_state.selected_plan = plan
                st.session_state.day = 1
                st.session_state.current_topic = get_daily_topic()

    if "selected_plan" not in st.session_state:
        return

    st.success(f"Current Plan: {st.session_state.selected_plan}")

    today_topic = st.session_state.current_topic

    st.info(f"📌 Today's Topic:\n\n{today_topic}")

    essay_input = st.text_area(
        "✍️ Write your essay here",
        height=250
    )

    uploaded_file = st.file_uploader(
        "🎙️ Upload Audio (WAV recommended)",
        type=["wav"]
    )

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_path = temp_audio.name

        st.write("Processing audio...")

        spoken_text = speech_to_text(temp_path)

        st.text_area(
            "Recognized Text",
            value=spoken_text,
            height=150
        )

    level = st.selectbox(
        "Select Your Level",
        ["A1", "A2", "B1", "B2", "C1"]
    )

    if st.button("🚀 Submit for Feedback"):

        if not essay_input.strip():
            st.warning("Please write an essay first.")
            return

        if not is_topic_related(essay_input, today_topic):
            st.warning(
                "⚠️ Your essay appears unrelated to the topic. Feedback will still be generated."
            )

        with st.spinner("Analyzing your essay..."):
            feedback = get_feedback(essay_input, level)

        st.subheader("🔍 Feedback")
        st.markdown(feedback)

        feedback_analysis = analyze_feedback(feedback)

        labels = list(feedback_analysis.keys())
        sizes = list(feedback_analysis.values())

        if sum(sizes) > 0:
            fig, ax = plt.subplots(figsize=(5, 5))

            ax.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90
            )

            st.pyplot(fig)

        if st.button("🔄 Improve Further"):

            improvement_prompt = f"""
Improve the following essay for a {level} level student.
Keep the same topic but make grammar, vocabulary,
and cohesion stronger.

Essay:

{essay_input}
"""

            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert academic writing coach."
                        },
                        {
                            "role": "user",
                            "content": improvement_prompt
                        }
                    ],
                    temperature=0.5,
                    max_completion_tokens=1500
                )

                improved_version = response.choices[0].message.content

                st.subheader("✨ Improved Essay")
                st.markdown(improved_version)

            except Exception as e:
                st.error(str(e))


if __name__ == "__main__":
    app()
