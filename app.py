import streamlit as st
import google.generativeai as genai
import base64
import re
import streamlit.components.v1 as components
import requests
import json
import random

# --- CONFIG ---
st.set_page_config(page_title="VidyAI++ - AI Tutor", page_icon="📚", layout="wide")
genai.configure(api_key="AIzaSyA6q9q7UlGHvqi_133mbURPEeGlz0pJfe0")
YOUTUBE_API_KEY = "AIzaSyBf_8orgxubdwfPMhrPwG--e1LhTeSo6Z0"

model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNCTIONS ---
def get_gemini_response(query, difficulty, language):
    prompt = f"""
You are an AI tutor helping students in India.
Please answer the following question clearly and simply in {language} at a {difficulty} level.
If relevant, also suggest a related image using a direct image URL (like from Wikimedia or Unsplash).

Question: {query}

Return format:
Answer: <your answer>
Image: <image URL if relevant, else write 'None'>
"""
    response = model.generate_content(prompt).text

    answer_match = re.search(r"(?i)answer\s*:\s*(.+?)(?:\nimage\s*:|\Z)", response, re.DOTALL)
    image_match = re.search(r"(?i)image\s*:\s*(.*?)(?:\n|$)", response)

    answer_text = answer_match.group(1).strip() if answer_match else "Sorry, I couldn't find an answer."
    image_url = image_match.group(1).strip() if image_match else None

    return answer_text, image_url

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_youtube_videos(query, max_results=3):
    url = f"https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
    else:
        st.error(f"Failed to fetch data from YouTube API. Status code: {response.status_code}")
        return []

    videos = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        thumbnail = item["snippet"]["thumbnails"].get("high", {}).get("url", "")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        if thumbnail:
            videos.append({"title": title, "url": video_url, "thumbnail": thumbnail})

    return videos

# --- UI ---
img_base64 = get_base64_image("image.png")
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.9)),
                    url("data:image/png;base64,{img_base64}") no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style="text-align: center; color: #1e88e5; font-size: 40px;">🎓📘 Welcome to <span style="color:#1565c0;">VidyAI++</span> AI Tutor</h1>
    <h4 style="text-align: center; color: #444; font-size: 20px;">💡 A multilingual, AI-powered tutor for every learner in India 🇮🇳</h4>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #fff3e0; padding: 20px; border-radius: 15px;">
    🏫 <b>VidyAI++</b> is built for students in government schools and low-income areas. 📚 Ask anything and get personalized, easy-to-understand answers – in your own language!
</div>
""", unsafe_allow_html=True)

st.markdown("## ✏️ Ask Your Question")
query = st.text_input("📝 What would you like to learn today?", "")
col1, col2 = st.columns(2)
with col1:
    difficulty = st.selectbox("📊 Choose Difficulty Level:", ["Easy", "Medium", "Hard"], index=1)
with col2:
    language = st.selectbox("🌐 Choose Language:", ["English", "Telugu", "Hindi", "Bengali", "Marathi", "Tamil"], index=0)

voice_enabled = st.checkbox("🔊 Enable Voice Output", value=True)

if st.button("🎓 Get My Answer"):
    if query:
        with st.spinner("🎯 Thinking... Getting your answer..."):
            answer, image_url = get_gemini_response(query, difficulty, language)

        st.success("✅ Here's your personalized answer:")
        st.markdown(f"<div style='background-color:#e8f5e9;padding:20px;border-radius:10px;'>{answer}</div>", unsafe_allow_html=True)

        if voice_enabled:
            lang_map = {
                "English": "en-IN",
                "Hindi": "hi-IN",
                "Telugu": "te-IN",
                "Tamil": "ta-IN",
                "Marathi": "mr-IN",
                "Bengali": "bn-IN"
            }
            voice_lang = lang_map.get(language, "en-IN")
            components.html(f"""
                <script>
                    const synth = window.speechSynthesis;
                    const textToSpeak ={json.dumps(answer)};
                    const utterThis = new SpeechSynthesisUtterance(textToSpeak);
                    utterThis.lang = "{voice_lang}";
                    synth.speak(utterThis);
                </script>
            """, height=0)

        if image_url and image_url.lower() != "none" and image_url.startswith("http"):
            st.image(image_url, caption="🖼️ Related Visual",use_container_width=True)
        else:
            st.warning("⚠️ No valid image URL found.")

# Tabs section
tabs = ["Answer", "Related youtube Tutorials", "quize", "AI Mentor Matchmaking"]
tab = st.selectbox("📚OTHER OPTIONS🧠📽️", tabs)

if tab == "Related youtube Tutorials":
    st.markdown("## 🎥 YouTube Video Tutorials")
    if st.button("🎥 Show Related Videos"):
        videos = get_youtube_videos(query)
        for vid in videos:
            st.markdown(f"""
                <a href="{vid['url']}" target="_blank">
                    <div style="margin-bottom:20px; background-color: #e8f5e9; padding: 20px; border-radius: 12px;">
                        <img src="{vid['thumbnail']}" width="200px" style="border-radius: 10px; float: left; margin-right: 20px;">
                        <p style="font-size: 18px;">{vid['title']}</p>
                    </div>
                </a>
            """, unsafe_allow_html=True)

elif tab == "quize":
    st.markdown("## 🧩 Educational quiz")
    subject = st.selectbox("📚 Choose a subject to play quiz on:", ["Math", "Science", "English Vocabulary", "General Knowledge"])

    if subject == "Math":
        if "math_q" not in st.session_state:
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            st.session_state.math_q = f"What is {a} + {b}?"
            st.session_state.math_ans = a + b

        user_ans = st.number_input(st.session_state.math_q, step=1)
        if st.button("✅ Check Answer (Math)"):
            if int(user_ans) == st.session_state.math_ans:
                st.success("🎉 Correct!")
            else:
                st.error(f"❌ It's {st.session_state.math_ans}")
            del st.session_state.math_q
            del st.session_state.math_ans

    elif subject == "Science":
        questions = {"What gas do plants breathe in?": "Carbon dioxide"}
        if "sci_q" not in st.session_state:
            q, correct = random.choice(list(questions.items()))
            st.session_state.sci_q = q
            st.session_state.sci_ans = correct

        user_ans = st.text_input(st.session_state.sci_q)
        if st.button("✅ Check Science Answer"):
            if user_ans.strip().lower() == st.session_state.sci_ans.lower():
                st.success("🎉 Correct!")
            else:
                st.error(f"❌ It's {st.session_state.sci_ans}")
            del st.session_state.sci_q
            del st.session_state.sci_ans

    elif subject == "English Vocabulary":
        vocab = {"Happy": "Feeling joy"}
        if "eng_q" not in st.session_state:
            word, correct = random.choice(list(vocab.items()))
            st.session_state.eng_q = word
            st.session_state.eng_ans = correct

        user_ans = st.text_input(f"What is the meaning of '{st.session_state.eng_q}'?")
        if st.button("✅ Check English Answer"):
            if st.session_state.eng_ans.lower() in user_ans.strip().lower():
                st.success("🎉 Great!")
            else:
                st.error(f"❌ It's '{st.session_state.eng_ans}'")
            del st.session_state.eng_q
            del st.session_state.eng_ans

    elif subject == "General Knowledge":
        gk = {"What is the capital of India?": "New Delhi"}
        if "gk_q" not in st.session_state:
            q, correct = random.choice(list(gk.items()))
            st.session_state.gk_q = q
            st.session_state.gk_ans = correct

        user_ans = st.text_input(st.session_state.gk_q)
        if st.button("✅ Check GK Answer"):
            if user_ans.strip().lower() == st.session_state.gk_ans.lower():
                st.success("🎉 Correct!")
            else:
                st.error(f"❌ It's {st.session_state.gk_ans}")
            del st.session_state.gk_q
            del st.session_state.gk_ans

elif tab == "AI Mentor Matchmaking":
    st.markdown("## 🤝 AI Mentor Matchmaking System")
    emotion = st.selectbox("💬 How are you feeling today?", ["Happy", "Confused", "Stressed", "Excited", "Neutral"])
    subject_need = st.selectbox("📘 What subject do you need help with?", ["Math", "Science", "English", "Any"])
    region = st.selectbox("📍 Your region/state:", ["Telangana", "Maharashtra", "West Bengal", "Tamil Nadu", "Bihar", "Uttar Pradesh", "Other"])
    availability = st.selectbox("⏰ When are you available for mentorship?", ["Morning", "Afternoon", "Evening", "Flexible"])

    if st.button("🔍 Find My Mentor"):
        mentors = [
            {"name": "Anita Sharma", "subject": "Math", "region": "Uttar Pradesh", "lang": "Hindi", "emotion_fit": "Stressed"},
            {"name": "Ravi Kumar", "subject": "Science", "region": "Tamil Nadu", "lang": "Tamil", "emotion_fit": "Confused"},
            {"name": "Fatima Begum", "subject": "English", "region": "West Bengal", "lang": "Bengali", "emotion_fit": "Neutral"},
            {"name": "Ajay Patel", "subject": "Any", "region": "Maharashtra", "lang": "Marathi", "emotion_fit": "Happy"},
            {"name": "Sushma Reddy", "subject": "Any", "region": "Telangana", "lang": "Telugu", "emotion_fit": "Excited"}
        ]
        matches = [m for m in mentors if 
                   (m["subject"] == subject_need or m["subject"] == "Any") and
                   (m["region"] == region or region == "Other") and
                   (m["emotion_fit"] == emotion or m["emotion_fit"] == "Neutral")]
        if matches:
            chosen = random.choice(matches)
            st.success("🎉 Mentor Found!")
            st.markdown(f"""
                <div style='background-color:#e8f5e9;padding:20px;border-radius:10px;color:#1b5e20;font-size:18px;'>
                    👩‍🏫 <b>Name:</b> {chosen['name']} <br>
                    📘 <b>Subject:</b> {chosen['subject']} <br>
                    🌐 <b>Language:</b> {chosen['lang']} <br>
                    📍 <b>Region:</b> {chosen['region']} <br>
                    💬 <b>Best For:</b> Feeling {chosen['emotion_fit']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No mentor match found. Please try again with different inputs.")

# Footer
st.markdown("""
    <hr>
    <footer style="text-align: center; font-size: 16px; color: #777;">
        🧠 Made with ❤️ for students under the NEP | &copy; 2025 VidyAI++ 🚀
    </footer>
""", unsafe_allow_html=True)