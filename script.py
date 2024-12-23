import os
import csv
import asyncio
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# YouTube API key
API_KEY = 'AIzaSyDGj5YaSUytxcyS5KK_s9wIE3I0RO_pr4g'

# Initialize the YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)


# Function to fetch video details
async def fetch_video_details(video_id):
    try:
        # Get the video details
        video_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()

        # Extract relevant details
        video = video_response['items'][0]
        title = video['snippet']['title']
        description = video['snippet']['description']
        channel_title = video['snippet']['channelTitle']
        tags = video['snippet'].get('tags', [])
        category = video['snippet']['categoryId']
        publish_date = video['snippet']['publishedAt']
        duration = video['contentDetails']['duration']
        view_count = video['statistics']['viewCount']
        comment_count = video['statistics'].get('commentCount', 0)

        # Fetch captions info
        captions = youtube.captions().list(part="snippet", videoId=video_id).execute()
        captions_available = 'True' if captions['items'] else 'False'
        caption_text = 'N/A'  # Would require additional processing to fetch captions text

        # Extract location (if available)
        location = video['snippet'].get('location', 'Unknown')

        return {
            'Video URL': f"https://www.youtube.com/watch?v={video_id}",
            'Title': title,
            'Description': description,
            'Channel Title': channel_title,
            'Keyword Tags': tags,
            'YouTube Video Category': category,
            'Topic Details': 'N/A',  # Placeholder, depends on the content
            'Video Published at': publish_date,
            'Video Duration': duration,
            'View Count': view_count,
            'Comment Count': comment_count,
            'Captions Available': captions_available,
            'Caption Text': caption_text,
            'Location of Recording': location
        }
    except HttpError as err:
        print(f"Error fetching video details: {err}")
        return None


# Function to fetch top 500 videos based on genre/category
async def fetch_top_videos(genre):
    video_list = []
    try:
        search_response = youtube.search().list(
            q=genre,
            type='video',
            part='snippet',
            maxResults=50
        ).execute()

        # Paginate and collect top 500 videos
        for item in search_response['items']:
            video_id = item['id']['videoId']
            video_details = await fetch_video_details(video_id)
            if video_details:
                video_list.append(video_details)

        # Store the collected data in a CSV file
        df = pd.DataFrame(video_list)
        df.to_csv('top_500_videos.csv', index=False)
        print("CSV file saved successfully.")

    except HttpError as err:
        print(f"Error fetching videos: {err}")


# Main execution
async def main():
    genre = input("Enter the genre: ")  # Dynamic input for genre
    await fetch_top_videos(genre)


if __name__ == '__main__':
    asyncio.run(main())