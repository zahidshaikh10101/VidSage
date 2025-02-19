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
import os
import requests

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
        time.sleep(2)
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
st.sidebar.title("VidSage 🎬")
option = st.sidebar.selectbox("🔍 Select Page", ["📄 Video Summarizer", "📊 Video Analyzer", "⬇️ Video Downloader"])

if option == "📄 Video Summarizer":
    st.title("VidSage 🎬")
    st.subheader("YouTube Video Summarizer 🎥📄")
    st.markdown("📝 Extract and summarize from YouTube videos.")

    # Input fields
    youtube_video_url = st.text_input("🔗 Enter YouTube Video URL")
    sum_length = st.slider("📏 Enter Summary Length (words)", min_value=100, max_value=5000, step=100, value=100)

    if st.button("📝 Generate Summary"):
        if not youtube_video_url:
            st.warning("⚠️ Please enter a valid YouTube URL.")
        elif not validate_youtube_url(youtube_video_url):
            st.error("❌ Invalid YouTube URL! Please enter a valid YouTube video link.")
        else:
            vid_id = video_id(youtube_video_url)
            
            # Custom progress indicator
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            transcript = extract_transcript(vid_id, progress_text)
            summary = summarize_transcript(transcript, sum_length, progress_bar, progress_text)

            # Display summary in markdown for better formatting
            st.subheader("📜 Summary")
            st.markdown(summary, unsafe_allow_html=True)  # Allows HTML for better formatting
            
            # Add download PDF button
            pdf = create_pdf(summary)
            st.download_button(
                label="📥 Download Summary as PDF",
                data=pdf,
                file_name="summary.pdf",
                mime="application/pdf"
            )

elif option == "📊 Video Analyzer":
    st.title("VidSage 🎬")
    st.subheader("YouTube Video Analyzer 🔍📊")
    st.markdown("📊 Get various details and insights from a YouTube video.")

    youtube_video_url = st.text_input("🔗 Enter YouTube Video URL for Analysis")

    if st.button("🔍 Analyze Video"):
        if not youtube_video_url:
            st.warning("⚠️ Please enter a valid YouTube URL.")
        elif not validate_youtube_url(youtube_video_url):
            st.error("❌ Invalid YouTube URL! Please enter a valid YouTube video link.")
        else:
            vid_id = video_id(youtube_video_url)
            
            # Fetch video details from API
            api_url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
            querystring = {"videoId": vid_id}
            headers = {
                "x-rapidapi-key": "702a4be6f6msh4fbca242aae430ap194bcfjsn87401b780075",
                "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com"
            }

            response = requests.get(api_url, headers=headers, params=querystring)
            if response.status_code == 200:
                video_data = response.json()
                
                # Parse JSON response
                video_id = video_data.get("id", "N/A")
                title = video_data.get("title", "N/A")
                description = video_data.get("description", "N/A")
                channel_name = video_data.get("channel", {}).get("name", "N/A")
                length_in_sec = video_data.get("lengthSeconds", "N/A")
                views = video_data.get("viewCount", "N/A")
                likes = video_data.get("likeCount", "N/A")
                publish_date = video_data.get("publishedTimeText", "N/A")
                comments = video_data.get("commentCountText", "N/A")
                thumbnail = video_data.get("thumbnails", [{}])[4].get("url", "")
                videos = video_data.get("videos", {}).get("items", [])  # Ensure items is a list
                download_url = videos[0]["url"] if videos else ""

                
                # Display video details
                st.image(thumbnail, width=700)
                st.markdown(f"<h2 style='font-size:24px;'><b>🎬 Title:</b> {title}</h2>", unsafe_allow_html=True)
                st.markdown('---')
                st.markdown(f"<p style='font-size:20px;'><b>📝 Description:</b></p> {description}", unsafe_allow_html=True)
                st.markdown('---')

                # Create three columns for Channel Name, Duration, and Published Date
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<p style='font-size:18px;'><b>📺 Channel Name:</b> {channel_name}</p>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<p style='font-size:18px;'><b>⏳ Duration:</b> {length_in_sec} seconds</p>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<p style='font-size:18px;'><b>📅 Published Date:</b> {publish_date}</p>", unsafe_allow_html=True)

                # Create three columns for Likes, Views, and Comments
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.markdown(f"<p style='font-size:18px;'><b>👍 Likes:</b> {likes}</p>", unsafe_allow_html=True)
                with col5:
                    st.markdown(f"<p style='font-size:18px;'><b>👀 Views:</b> {views}</p>", unsafe_allow_html=True)
                with col6:
                    st.markdown(f"<p style='font-size:18px;'><b>💬 Comments:</b> {comments}</p>", unsafe_allow_html=True)
                st.markdown('---')

                st.subheader("📌 Recommended Videos")
                related_videos = video_data.get("related", {}).get("items", [])

                if related_videos:
                    for i in range(min(10, len(related_videos))):  # Fetch top 7 related videos
                        related = related_videos[i]
                        video_url = f"https://www.youtube.com/watch?v={related.get('id', 'N/A')}"
                        title = related.get("title", "N/A")
                        channel = related.get("channel", {}).get("name", "N/A")
                        duration = related.get("lengthText", "N/A")
                        views = related.get("viewCountText", "N/A")
                        publish = related.get("publishedTimeText", "N/A")
                        thumbnail = related.get("thumbnails", [{}])[0].get("url", "")

                        # Box container with border
                        st.markdown(
                            f"""
                            <div style="border: 1px solid #444; padding: 10px; border-radius: 8px; margin-bottom: 10px; background-color: #222;">
                                <p><a href="{video_url}" style="font-size:18px; font-weight:bold; text-decoration:none; color:#1E90FF;">🎥 {title}</a></p>
                                <div style="display: flex; align-items: center;">
                                    <img src="{thumbnail}" width="180px" style="border-radius: 5px; margin-right: 15px;">
                                    <div>
                                        <p style="margin: 5px 0;"><b>📺 Channel:</b> {channel}</p>
                                        <p style="margin: 5px 0;"><b>⏳ Duration:</b> {duration}</p>
                                        <p style="margin: 5px 0;"><b>👀 Views:</b> {views}</p>
                                        <p style="margin: 5px 0;"><b>📅 Published:</b> {publish}</p>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.warning("⚠️ No related videos found.")
            else:
                st.error("❌ Failed to fetch video details. Please try again later.")

elif option == "⬇️ Video Downloader":
    st.title("VidSage 🎬")
    st.subheader("YouTube Video Downloader 🔍📊")
    st.markdown("🛠️ Download YouTube videos in various formats easily.")

    youtube_video_url = st.text_input("🔗 Enter YouTube Video URL for Analysis")

    if st.button("🔍 Analyze Video"):
        if not youtube_video_url:
            st.warning("⚠️ Please enter a valid YouTube URL.")
        elif not validate_youtube_url(youtube_video_url):
            st.error("❌ Invalid YouTube URL! Please enter a valid YouTube video link.")
        else:
            vid_id = video_id(youtube_video_url)