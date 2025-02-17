import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import time
import re
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch

# Configure Google Generative AI
genai.configure(api_key="AIzaSyBe8oTPpsp8m3u1wshx9r2ahICrGWwqYrc")

# Function to validate YouTube URL
def validate_youtube_url(url):
    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?'
        r'(youtube\.com/watch\?v=|youtu\.be/)'
        r'[\w-]{11}$'
    )
    return bool(youtube_regex.match(url))

# Function to extract Video ID
def video_id(youtube_video_url):
    return youtube_video_url.split("v=")[-1][:11] if "v=" in youtube_video_url else youtube_video_url.split("/")[-1][:11]

# Function to extract transcript from YouTube video
def extract_transcript(video_id, progress_text):
    try:
        progress_text.text("Extracting transcript... ⏳")
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([i["text"] for i in transcript_text])
    except Exception as e:
        return f"Error extracting transcript: {e}"

# Function to summarize transcript
def summarize_transcript(transcript, sum_length, progress_bar, progress_text):
    prompt = f"""
    You are a YouTube video summarizer. Your task is to summarize the given transcript into key points within {sum_length} words. 

    **Formatting Guidelines:**
    - Use **bold formatting** for important keywords, concepts, and section titles.
    - Structure the summary with **bullet points** or **numbered lists** for clarity.
    - Maintain proper indentation and spacing for readability.

    **Transcript:**
    {transcript}
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-01-21",
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        },
    )

    chat_session = model.start_chat()
    
    # Simulating progress for UI experience
    progress_text.text("Summarizing content... 📄")
    for percent in range(1, 101, 10):
        time.sleep(0.2)  # Simulating processing time
        progress_bar.progress(percent)

    response = chat_session.send_message(prompt)
    
    # Clear the progress bar
    progress_bar.empty()
    progress_text.empty()

    return response.text if response else "Error generating summary"

# Function to create PDF
def create_pdf(summary_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    story = []
    for line in summary_text.split('\n'):
        line = line.strip()  # Remove leading/trailing whitespace
        if line.startswith("**"):  # Bold text
            p = Paragraph(line, styles["h2"]) # Use heading 2 style for bold text
        elif line.startswith("* "):  # Bullet point
            p = Paragraph(f"• {line[2:]}", style) # Add bullet character and remove "* "
        else: # Normal text
            p = Paragraph(line, style)
        story.append(p)
        story.append(Spacer(1, 0.2*inch))  # Add spacing after each paragraph
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Streamlit App UI
st.title("YouTube Video Summarizer 🎥📄")
st.markdown("Extract and summarize from YouTube videos.")

# Input fields
youtube_video_url = st.text_input("Enter YouTube Video URL")
sum_length = st.slider("Enter Summary Length (words)", min_value=100, max_value=5000, step=100, value=100)

if st.button("Generate Summary"):
    if not youtube_video_url:
        st.warning("Please enter a valid YouTube URL.")
    elif not validate_youtube_url(youtube_video_url):
        st.error("Invalid YouTube URL! Please enter a valid YouTube video link.")
    else:
        vid_id = video_id(youtube_video_url)
        
        # Custom progress indicator
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        transcript = extract_transcript(vid_id, progress_text)
        summary = summarize_transcript(transcript, sum_length, progress_bar, progress_text)

        # Display summary in markdown for better formatting
        st.subheader("Summary")
        st.markdown(summary, unsafe_allow_html=True)  # Allows HTML for better formatting
        
        # Add download PDF button
        pdf = create_pdf(summary)
        st.download_button(
            label="Download Summary as PDF",
            data=pdf,
            file_name="summary.pdf",
            mime="application/pdf"
        )
