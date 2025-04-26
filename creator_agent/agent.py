from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
import os
import requests
import random

YOUTUBE_VIDEO_BASE_URL = "https://www.youtube.com/watch?v="


def fetch_youtube_videos():
    """Fetches video details from a YouTube channel using the YouTube Data API."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    playlist_id = os.getenv("YOUTUBE_PLAYLIST_UPLOAD_ID")

    if not api_key or not playlist_id:
        raise ValueError(
            "YOUTUBE_API_KEY and YOUTUBE_PLAYLIST_UPLOAD_ID environment variables must be set.")

    try:
        response = requests.get(
            f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={api_key}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching YouTube videos: {e}")


def choose_random_video_url():
    """Chooses a random video URL from the fetched YouTube videos."""
    video_data = fetch_youtube_videos()
    if not video_data or "items" not in video_data:
        raise ValueError("No videos found in the YouTube playlist.")

    videos = video_data["items"]
    if not videos:
        raise ValueError("No videos found in the YouTube playlist.")

    random_video = random.choice(videos)
    video_id = random_video["snippet"]["resourceId"]["videoId"]
    return f"{YOUTUBE_VIDEO_BASE_URL}{video_id}"


def extract_video_transcript(video_url: str):
    """Extracts text transcript from a YouTube video using a Gemini model."""

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variables must be set.")

    client = genai.Client(api_key=api_key)

    content = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(file_uri=video_url, mime_type="video/*"),
                types.Part.from_text(text="Extract the text from this video.")
            ]
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"]
    )

    transcript = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-001",
        contents=content,
        config=generate_content_config,
    ):
        transcript += chunk.text
    return transcript


list_videos_agent = LlmAgent(
    model="gemini-2.5-flash-preview-04-17",
    name="list_videos_agent",
    description="Lists videos from a Youtube playlist.",
    instruction="Provide a list of available YouTube videos.",
    tools=[fetch_youtube_videos],
    output_key="videos"
)

choose_video_agent = LlmAgent(
    model="gemini-2.5-flash-preview-04-17",
    name="choose_video_agent",
    description="Chooses a random video from a Youtube playlist.",
    instruction=f"Choose a random video from the fetched list and return its URL (e.g., {YOUTUBE_VIDEO_BASE_URL}dQw4w9WgXcQ). Only save on the output_key the video_url",
    tools=[choose_random_video_url],
    output_key="video_url"
)

extract_text_agent = LlmAgent(
    model="gemini-2.5-flash-preview-04-17",
    name="extract_text_agent",
    description="Extracts the transcription of a video URL from the agent's state.",
    instruction="Get the video URL from the 'video_url' key in the agent's state, and use that URL to extract the video's transcription. Ensure the correct URL is used for the transcription process.",
    tools=[extract_video_transcript],
    output_key="extracted_text"
)

script_agent = LlmAgent(
    model="gemini-2.5-flash-preview-04-17",
    name="script_agent",
    description="Transforms extracted text into a voiceover script for short videos.",
    instruction="""
    Using the extracted text in 'extracted_text', identify and focus on the **most engaging section** or a **specific topic** discussed within the text (do not attempt to summarize the entire video).

    Then, create a concise, highly engaging voiceover script for a short video (suitable for platforms like YouTube Shorts, Instagram Reels, TikTok) based on that selected portion, tailoring the language and tone specifically for a **female audience**. The script should flow naturally for voiceover and grab attention quickly.

    Ensure the script's communication style is **direct, simple, animated, engaging, and inclusive**, reflecting your own style.
    """,
    output_key="generated_script"
)


demo_multi_agent = LlmAgent(
    model="gemini-2.5-flash-preview-04-17",
    name="creator_agent",
    description="Orchestrates agents to generate voiceover scripts for short videos based on YouTube channel content.",
    instruction="""
    You are an AI agent designed to assist Simara (who prefers to be called Si) with tasks related to her specific YouTube channel content, particularly generating assets for short videos.

    User Identity: Your user is Simara, and she explicitly prefers to be addressed as Si. Always refer to her as 'Si' in your interactions.

    Agent Autonomy & Workflow: You have the autonomy to determine the necessary steps and call the appropriate sub-agents to fulfill Si's requests, such as generating a voiceover script for a short video, providing transcripts. You must decide the optimal workflow based on Si's request and the available tools (sub-agents).

    Channel Access: You have access to information specifically about Si's YouTube channel. To retrieve the list of videos from her channel, you must call the list_videos_agent. This agent is the designated tool for listing videos from Si's channel, and you should always use it for this purpose. Do not attempt to list videos from arbitrary or other YouTube channels.

    Operational Dependencies: When processing Si's requests, adhere to the following workflow dependencies:

    If you need to choose a specific video from Si's channel, you must first list the videos using the list_videos_agent.
    If you need to create a transcript for a video, you must first have chosen a specific video.
    Core Task: Based on Si's request and following the dependencies and agent calling rules outlined above, determine the required steps and sub-agents to ultimately generate the requested output, such as a voiceover script for a short video derived from her channel's content.

    Instruction Summary:

    Address the user as 'Si'.
    Act autonomously to plan and execute the steps needed to fulfill Si's request.
    Decide which sub-agents to call and when.
    Always call the list_videos_agent when you need the list of videos from Si's specific channel.
    Follow the dependency chain: List -> Choose -> Transcript
    Generate the requested output (e.g., short video script) by managing this workflow.
    """,
    sub_agents=[
        list_videos_agent,
        choose_video_agent,
        extract_text_agent,
        script_agent
    ],
)

root_agent = demo_multi_agent
