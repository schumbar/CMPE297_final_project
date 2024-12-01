# ===============================
# File: main.py
# ===============================
import streamlit as st
import time
from agents import PodcastAnalyzer
from config import OPENAI_API_KEY, PPLX_API_KEY
import os

def initialize_api_keys():
    """Initialize API keys from environment or user input"""
    openai_api_key = OPENAI_API_KEY
    perplexity_api_key = PPLX_API_KEY

    if not openai_api_key:
        openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
        if not openai_api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
            return None, None

    if not perplexity_api_key:
        perplexity_api_key = st.sidebar.text_input("Enter Perplexity API Key", type="password")
        if not perplexity_api_key:
            st.error("Please enter your Perplexity API key in the sidebar.")
            return None, None

    return openai_api_key, perplexity_api_key

def display_sidebar():
    """Display sidebar information"""
    st.sidebar.title("How it Works")
    
    st.sidebar.markdown("""
    Welcome to ⏯️ **Video Fact Finder**, a tool designed to help you:
        
    - Summarize key points from YouTube videos
    - Identify actionable insights and takeaways
    - Fact-check claims made in the video for accuracy
    - Provide detailed analysis of content

    Analyze your video content efficiently using AI-powered tools.

    *Note:* This tool analyzes only speech, so all results are based on transcription, not video.

    *Version 2.0.0*
    """)

def display_results(result: dict, elapsed_time: float):
    """Display analysis results in a structured format"""
    # Display raw transcript in expander
    with st.expander("Show Raw Transcript"):
        st.write(result['raw_transcript'])
    
    # Display the final analysis
    st.markdown(result['final_analysis'])
    
    # Display individual components in expanders
    with st.expander("Show Detailed Analysis"):
        st.write("### Summary")
        st.write(result['summary'])
        
        st.write("### Action Points")
        st.write(result['action_points'])
        
        st.write("### Claims")
        st.write(result['claims'])
        
        st.write("### Fact Check")
        st.write(result['fact_check'])
    
    st.success(f"Processing completed in {elapsed_time:.2f} seconds")

def run():
    """Main application function"""
    # Configure the page
    st.set_page_config(
        page_title="Video Fact Finder",
        page_icon="▶️",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    # Display the main title
    st.title("⏯️ Video Fact Finder")
    
    # Display sidebar information
    display_sidebar()
    
    # Initialize API keys
    openai_api_key, perplexity_api_key = initialize_api_keys()
    if not openai_api_key or not perplexity_api_key:
        return

    # Get YouTube URL input
    podcast_url = st.text_input(
        "Enter the YouTube URL of the video you want to analyze",
        help="Paste a YouTube URL here. The video should be publicly accessible."
    )

    # Display video preview if URL is valid
    if podcast_url:
        if "youtube.com" in podcast_url or "youtu.be" in podcast_url:
            if "shorts" not in podcast_url:  # Skip shorts as they might cause issues
                try:
                    st.video(podcast_url)
                except Exception:
                    st.error("Unable to load video preview. Please check if the URL is correct.")
            else:
                st.warning("YouTube Shorts are not supported at this time.")
        else:
            st.error("Please enter a valid YouTube URL")

    # Process button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        process_button = st.button("📋 Analyze Video", use_container_width=True)

    if process_button:
        if not podcast_url:
            st.error("Please enter a YouTube URL")
            return

        try:
            start_time = time.time()
            
            with st.spinner('Processing the video... this may take a few minutes.'):
                # Initialize analyzer and process video
                analyzer = PodcastAnalyzer(openai_api_key, perplexity_api_key)
                result = analyzer.analyze_podcast(podcast_url)
                
                # Calculate processing time
                elapsed_time = time.time() - start_time
                
                # Display results
                display_results(result, elapsed_time)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("If the error persists, please try with a different video or check your API keys.")

if __name__ == "__main__":
    run()