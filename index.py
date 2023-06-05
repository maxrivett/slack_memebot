# Import required modules
from flask import Flask, request, jsonify
import requests
import json
from slack_sdk import WebClient
import openai
import random
from dotenv import load_dotenv
import os

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
PROMPT = "You are tasked with crafting a funny meme. This meme will feature two text segments – one at the top and the other at the bottom. These two segments should be created by you and separated using the '|' symbol. The theme of the meme is '%s'. Maintain a light-hearted and humorous tone throughout. Please note, avoid using explicit labels like 'top text' or 'bottom text', and refrain from using quotation marks."
PROMPT_NO_INPUT = "You are tasked with crafting a funny meme. This meme will feature two text segments – one at the top and the other at the bottom. These two segments should be created by you and separated using the '|' symbol. Your task is to decide the theme and content of the meme. Maintain a light-hearted and humorous tone throughout. Please note, avoid using explicit labels like 'top text' or 'bottom text', and refrain from using quotation marks."

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
    print(random_meme['box_count'])
    if random_meme['box_count'] > 2 :
        return get_random_template_id()

    return random_meme['id']

# Define a route for the command endpoint 
@app.route('/meme-endpoint', methods=['POST'])
def create_meme():
    # Parse the request payload
    payload = request.form

    # Extract the user input from the payload and get a random meme template ID
    user_input = payload['text']
    template_id = get_random_template_id()
    if template_id == None :
        raise Exception("No template_id generated")

    # Set the prompt based on whether user input was provided
    prompt = PROMPT % (user_input) if user_input != "" else PROMPT_NO_INPUT

    # Generate meme phrase using GPT-4
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=60
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


    # Post meme to Slack channel
    client.chat_postMessage(
        channel=payload['channel_id'],
        text="Here's your meme:" if user_input == "" else "Here's your meme about " + user_input + ":",
        attachments=[{"image_url": meme_url, "text": meme_phrase}]
    )

    return jsonify(response_type='in_channel')

# Start the flask app
if __name__ == "__main__":
    app.run(debug=True)


