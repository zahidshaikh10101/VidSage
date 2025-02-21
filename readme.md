# VidSage

VidSage is a powerful and easy-to-use web application that provides three essential YouTube-related tools: **Video Summarizer**, **Video Analyzer**, and **Video Downloader**. This application enables users to quickly summarize videos, analyze video details, get recommendation on video and download videos or audio in various formats.

---

## Features

### 1. Video Summarizer
The **Video Summarizer** module allows users to generate concise summaries of YouTube videos.
- Enter the **YouTube URL**.
- Use the **word length slider** to select the number of words for the summary.
- Click on **Summarize** to generate the summary.
- Download the summarized content for future reference.

### 2. Video Analyzer
The **Video Analyzer** module extracts detailed information from a YouTube video.
- Enter the **YouTube URL**.
- Click on **Analyze** to fetch details such as:
  - **Thumbnail**
  - **Title**
  - **Description**
  - **Channel Name**
  - **Likes**
  - **Comments**
  - **Views**
  - **Publish Date**
- Additionally, based on the provided YouTube video, VidSage suggests **10 recommended videos**.

### 3. Video Downloader
The **Video Downloader** module allows users to download YouTube videos and audio in various formats.
- Enter the **YouTube URL**.
- Click on **Start Download**.
- Choose from multiple available formats:
  - **MP4**
  - **M4A**
  - **WEBM**
  - Other supported formats
- Choose from multiple quality.
- Download the video or audio file as per your requirement.

---

## YouTube URL Validation
VidSage includes **YouTube URL validation** to ensure that only correct YouTube links are processed. If an invalid URL is entered, a **warning message** is displayed to notify the user.

---

## Installation & Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/VidSage.git
   ```
2. Navigate to the project directory:
   ```bash
   cd VidSage
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```
5. Open your browser and go to:
   ```
   http://localhost:8000
   ```

---

## Screenshots


---

## Technologies Used
- **Python** (Streamlit, Pandas, ReportLab, Requests, Tqdm, Regular Expressions (re), io, os, time, datetime, json)
- **APIs** (YouTube Media Downloader, YouTube Transcript API, Google Generative AI (Gemini))

---

## Contribution
If you’d like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch (`feature-branch`).
3. Commit your changes.
4. Push to the branch and submit a Pull Request.

---

## Contact
For any queries or suggestions, feel free to reach out:
- **Email**: zahidshaikh10101@gmail.com
- **GitHub**: [zahidshaikh10101](https://github.com/zahidshaikh10101)

---

### Enjoy using VidSage! 🎥📌📥

