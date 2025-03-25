import streamlit as st
import google.generativeai as genai
import time

def configure_api():
    api_key = "YOUR GEMINI API KEY" 
    genai.configure(api_key=api_key)

def save_uploaded_file(uploaded_file):
    file_path = f"./{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def process_video(file_path):
    st.write("Uploading video for processing...")
    file = genai.upload_file(path=file_path)

    while file.state.name == "PROCESSING":
        st.write("Processing video...")
        time.sleep(20)
        file = genai.get_file(file.name)

    if file.state.name == "FAILED":
        st.error("Video processing failed. Please try again.")
        return None

    st.success("Video processing completed!")
    return file

def generate_video_summary(file, user_prompt):
    st.write("Generating response...")
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([user_prompt, file], request_options={"timeout": 600})
    
    return response.text

def analyze_moderation(summary_text):
    st.write("Analyzing content for moderation...")

    mod_prompt = f"Analyze this text and assign a percentage (0-100%) of inappropriate content:\n{summary_text}"
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    mod_response = model.generate_content(mod_prompt)

    try:
        mod_score = next((int(s) for s in mod_response.text.split() if s.isdigit()), 0)
    except ValueError:
        mod_score = 0

    if mod_score <= 25:
        classification = "Safe Content"
        st.success(f"Moderation Score: {mod_score}% - {classification}")
    elif 25 < mod_score <= 60:
        classification = "Needs Review"
        st.warning(f"Moderation Score: {mod_score}% - {classification}")
    else:
        classification = "Blocked (Inappropriate)"
        st.error(f"Moderation Score: {mod_score}% - {classification}")

def main():
    st.title("🎥 Video-to-Text Summarization & Content Moderation")

    configure_api()

    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "webm"])

    if uploaded_file is not None:
        st.write(f"📂 File uploaded: {uploaded_file.name}")

        user_prompt = st.text_area("✍️ Enter your request (e.g., 'Summarize key points', 'Extract dialogues')", 
                                   value="Summarize the content of the video.")
        
        if st.button("🔍 Process Video"):
            file_path = save_uploaded_file(uploaded_file)
            processed_file = process_video(file_path)

            if processed_file:
                summary_text = generate_video_summary(processed_file, user_prompt)
                st.subheader("Video Summary:")
                st.write(summary_text)

                analyze_moderation(summary_text)

if __name__ == "__main__":
    main()
