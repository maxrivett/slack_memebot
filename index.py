# Import required modules
from flask import Flask, request, jsonify
import requests
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
import random
from dotenv import load_dotenv
import os
import threading

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set OpenAI and Slack API keys from environment variables
openai.api_key = os.getenv("API_KEY")
slack_token = os.getenv("SLACK_TOKEN")

# Initialize Slack client with the API token
client = WebClient(token=slack_token)

# Set Imgflip username and password from environment variables
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

# Prompts for GPT API
PROMPT = "You are tasked with crafting a funny meme, using the %s meme format. Note that the meme should not be about the subject matter of the format, be sure to not include the meme format in any of the text. This meme will feature two text segments – one at the top and the other at the bottom. These two segments should be created by you and separated using the '|' symbol. The theme of the meme is '%s'. Maintain a light-hearted and humorous tone throughout. Please note, avoid using explicit labels like 'top text' or 'bottom text', and refrain from using quotation marks!"
PROMPT_NO_INPUT = "You are tasked with crafting a funny meme, using the %s meme format. Note that the meme should not be about the subject matter of the format, be sure to not include the meme format in any of the text. This meme will feature two text segments – one at the top and the other at the bottom. These two segments should be created by you and separated using the '|' symbol. Your task is to decide the theme and content of the meme. Maintain a light-hearted and humorous tone throughout. Please note, avoid using explicit labels like 'top text' or 'bottom text', and refrain from using quotation marks!"

# Function to get a random meme template ID from Imgflip
def get_random_template_id():
    url = "https://api.imgflip.com/get_memes"
    response = requests.get(url)
    data = response.json()

    # Check if the response was successful
    if response.status_code != 200 or not data.get('success', False):
        return None

    memes = data.get('data', {}).get('memes', [])
    if not memes:
        return None

    random_meme = random.choice(memes)
    # box_count > 2 not working with imgflip api so make sure it's less
    if random_meme['box_count'] > 2 :
        return get_random_template_id()

    return random_meme['id'], random_meme['name']

# Function to post the meme to chat (separated so that there is a loading message in the meantime)
def generate_and_post_meme(user_input, username, channel_id, ts):
    template_id, description = get_random_template_id()
    if template_id == None :
        raise Exception("No template_id generated")

    # Set the prompt based on whether user input was provided
    prompt = PROMPT % (description, user_input) if user_input != "" else PROMPT_NO_INPUT % (description)

    # Generate meme phrase using GPT-4
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.8,
        max_tokens=150
    )

    # Choose "best" meme option
    meme_phrase = response['choices'][0]['text'].strip().split('\n')[0]

    # Create meme using Imgflip API
    url = "https://api.imgflip.com/caption_image"
    meme_phrases = meme_phrase.split('|')
    params = {
        'template_id': str(template_id),  # ID of the meme template 
        'username': IMGFLIP_USERNAME,
        'password': IMGFLIP_PASSWORD,
        'font': "impact",
    }

    # Add texts dynamically (no longer useful after determining imgflip API only supports 2 text boxes)
    for i, phrase in enumerate(meme_phrases):
        params[f'text{i}'] = phrase
    res = requests.post(url, params)
    meme_url = json.loads(res.text)['data']['url']

    # Delete the "Creating your meme now..." message
    client.chat_delete(
        channel=channel_id,
        ts=ts
    )

    # Post meme to Slack channel
    client.chat_postMessage(
        channel=channel_id,
        text="Here's your meme, " + username + ":" if user_input == "" else "Here's your meme about " + user_input + "," + username + ":",
        attachments=[{"image_url": meme_url, "author_name": "_", "author_link": "https://www.maxrivett.com",}]
    )

        

# Define a route for the command endpoint 
@app.route('/meme-endpoint', methods=['POST'])
#
def create_meme():
    # Parse the request payload
    payload = request.form

    # Extract the user input from the payload and get a random meme template ID
    user_input = payload['text']
    channel_id = payload['channel_id']

    # Send the "Creating your meme now..." message
    response = client.chat_postMessage(
        channel=channel_id,
        text='Creating your meme now...'
    )

    username = ''
    # Get the user's username using the Slack API
    try:
        user_info = client.users_info(user=payload['user_id'])
        username = user_info['user']['name']
    except SlackApiError as e:
        username = 'Unknown User'
    
    # Get the 'ts' of the message we just sent
    ts = response['ts']

    threading.Thread(target=generate_and_post_meme, args=(user_input, username, channel_id, ts)).start()

    return '', 200  # Empty response, status code 200

# Start the flask app
if __name__ == "__main__":
    app.run(debug=True)