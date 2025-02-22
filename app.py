# code 01
import os
import streamlit as st
import random
import speech_recognition as sr
import matplotlib.pyplot as plt
from groq import Groq
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from googletrans import Translator

# Initialize Groq client with API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
translator = Translator()

# Sample Topics & AI Writing Samples
topics = [
    "Technology has made life easier or more complicated? Discuss both views.",
    "Should governments invest more in public transport?",
    "Does social media harm face-to-face communication?",
    "Should plastic be banned? Pros and Cons."
]
writing_samples = {
    "A1": "Technology is good. We use it every day. It helps us.",
    "B1": "Technology has both advantages and disadvantages. It makes tasks easier but can also lead to over-reliance.",
    "C1": "The advent of technology has streamlined numerous aspects of human life, yet it has simultaneously fostered certain dependencies."
}

# UI Sidebar
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Daily Challenge", "Writing Feedback", "Leaderboard", "AI Writing Samples"])

# Daily Topic & Writing Streak
if page == "Daily Challenge":
    st.title("🎯 Daily Writing Challenge")
    today_topic = random.choice(topics)
    st.info(f"📌 **Today's Topic:** {today_topic}")
    if "streak" not in st.session_state:
        st.session_state.streak = 0
    st.sidebar.write(f"🔥 Streak: {st.session_state.streak} days")

# Real-Time Voice Input
if page == "Writing Feedback":
    st.title("📝 AI Writing Feedback")
    language = st.selectbox("Choose Language", ["English", "Urdu", "French"])
    essay = st.text_area("✍️ Write your essay here", height=200)
    
    st.subheader("🎙️ Speak Your Essay")
    webrtc_ctx = webrtc_streamer(key="speech-to-text", mode=WebRtcMode.SENDRECV)
    if webrtc_ctx.audio_receiver:
        recognizer = sr.Recognizer()
        with sr.AudioFile("input_audio.wav") as source:
            audio = recognizer.record(source)
            try:
                essay = recognizer.recognize_google(audio)
                st.write("Recognized Text:", essay)
            except:
                st.write("Could not recognize speech.")
    
    level = st.selectbox("Select Your Level", ["A1", "A2", "B1", "B2", "C1"])
    
    if st.button("🚀 Submit for Feedback"):
        feedback = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Provide grammar, cohesion, and vocabulary feedback."},
                {"role": "user", "content": essay}
            ],
            model="llama3-8b-8192",
        )
        translated_feedback = translator.translate(feedback.choices[0].message.content, dest=language).text
        st.subheader("🔍 Feedback:")
        st.markdown(translated_feedback, unsafe_allow_html=True)
    
# Leaderboard System
if page == "Leaderboard":
    st.title("🏆 Top Writers Leaderboard")
    leaderboard = {"Alice": 15, "Bob": 10, "Charlie": 8}
    sorted_leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))
    for rank, (user, score) in enumerate(sorted_leaderboard.items(), 1):
        st.write(f"{rank}. **{user}** - {score} Essays")

# AI Writing Samples
if page == "AI Writing Samples":
    st.title("📖 AI-Generated Writing Samples")
    level = st.selectbox("Choose Proficiency Level", ["A1", "B1", "C1"])
    st.write(f"✍️ Example Essay for {level}: {writing_samples[level]}")


# code 00
# import os
# import streamlit as st
# import random
# import matplotlib.pyplot as plt
# import speech_recognition as sr
# from groq import Groq

# # Initialize Groq client with API key
# # client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# client = Groq(api_key="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")

# # List of daily topics
# topics = [
#     "Some people believe that technology has made life easier, while others think it has made life more complicated. Discuss both views.",
#     "Should governments invest more in public transport rather than in roads for private vehicles?",
#     "Do you agree or disagree: Social media has a negative impact on face-to-face communication?",
#     "The use of plastic should be banned. Discuss the advantages and disadvantages."
# ]

# def get_daily_topic():
#     return random.choice(topics)

# def is_topic_related(essay, topic):
#     essay_keywords = set(essay.lower().split()[:10]) if essay else set()  # First 10 words
#     topic_keywords = set(topic.lower().split()[:10])  # First 10 words
#     similarity = len(essay_keywords.intersection(topic_keywords)) / len(topic_keywords)
#     return similarity > 0.3  # 30% keyword match threshold

# @st.cache_data
# def get_feedback(essay, level):
#     system_prompt = """
#     You are an expert academic writer with 40 years of experience in providing concise but effective feedback.
#     Provide feedback in the following format:
    
#     🔴 **Grammar Mistakes:**
#     - Replace **[wrong word]** with **[correct word]** (Mistake type)
    
#     🟡 **Cohesion & Flow:**
#     - Instead of **[phrase]**, use **[better phrase]** for better clarity.
    
#     🟢 **Vocabulary Suggestions:**
#     - Use **[better word]** instead of **[simple word]**.
    
#     📌 **Final Summary:**
#     - Bullet point summary of main improvements.
#     """
#     chat_completion = client.chat.completions.create(
#         messages=[{"role": "system", "content": system_prompt},
#                   {"role": "user", "content": essay}],
#         model="llama3-8b-8192",
#     )
#     return chat_completion.choices[0].message.content

# def analyze_feedback(feedback):
#     sections = {
#         "Grammar": feedback.count("🔴 **Grammar Mistakes:**"),
#         "Cohesion": feedback.count("🟡 **Cohesion & Flow:**"),
#         "Vocabulary": feedback.count("🟢 **Vocabulary Suggestions:**"),
#         "Structure": feedback.count("📌 **Final Summary:**"),
#     }
#     return sections  # Return dictionary with counts

# def speech_to_text(audio_path):
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(audio_path) as source:
#         st.write("Processing Audio...")
#         audio = recognizer.record(source)
#         try:
#             return recognizer.recognize_google(audio)
#         except:
#             return "Sorry, I couldn't understand the audio."

# def app():
#     st.title("EssayElevate - Writing Assistant for IELTS, DET, TOEFL")
    
#     st.header("📅 Choose Your Study Plan")
#     plan_columns = st.columns(3)
#     plans = ["30 Days Plan", "45 Days Plan", "60 Days Plan"]
#     for i, plan in enumerate(plans):
#         with plan_columns[i]:
#             st.subheader(plan)
#             st.write(f"Get daily writing topics for {plan}.")
#             if st.button(f"Select {plan}"):
#                 st.session_state.selected_plan = plan
#                 st.session_state.day = 1
    
#     if 'selected_plan' in st.session_state:
#         st.subheader(f"Current Plan: {st.session_state.selected_plan}")
        
#         today_topic = st.session_state.get("current_topic", get_daily_topic())
#         st.session_state.current_topic = today_topic
#         st.info(f"📌 **Today's Topic:** {today_topic}")

#         essay_input = st.text_area("✍️ Write your essay here", key="essay_input", height=200)
        
#         uploaded_file = st.file_uploader("🎙️ Upload an audio file", type=["wav", "mp3"])
        
#         if uploaded_file:
#             with open("input_audio.wav", "wb") as f:
#                 f.write(uploaded_file.getbuffer())
#             st.write("Processing your audio...")
#             spoken_text = speech_to_text("input_audio.wav")
#             st.write(f"Recognized Text: {spoken_text}")

#         level = st.selectbox("Select Your Level", ["A1", "A2", "B1", "B2", "C1"])

#         if "allow_feedback" not in st.session_state:
#             st.session_state.allow_feedback = False  # Prevent auto feedback

#         if st.button("🚀 Submit for Feedback"):
#             if not is_topic_related(essay_input, today_topic):
#                 st.warning("⚠️ Your essay seems unrelated to the given topic. Please review.")
#                 if st.button("Proceed Anyway"):
#                     st.session_state.allow_feedback = True  # Now allow feedback
#             else:
#                 st.session_state.allow_feedback = True

#         if st.session_state.allow_feedback:
#             feedback = get_feedback(essay_input, level)
#             st.subheader("🔍 Feedback:")
#             st.markdown(feedback, unsafe_allow_html=True)

#             feedback_analysis = analyze_feedback(feedback)
#             labels = list(feedback_analysis.keys())
#             sizes = list(feedback_analysis.values())

#             if sum(sizes) > 0:
#                 fig, ax = plt.subplots()
#                 ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
#                 st.pyplot(fig)

#             if st.button("🔄 Improve Further"):
#                 improved_version = get_feedback(feedback, level)
#                 st.subheader("🔹 Suggested Improved Version:")
#                 st.markdown(improved_version, unsafe_allow_html=True)

#             st.session_state.day += 1

# if __name__ == "__main__":
#     app()
