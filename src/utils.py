import requests
import openai
import random
import json
from config import Config

PROMPT = "You are tasked with crafting a funny meme, using the %s meme format. Note that the meme should not be about the subject matter of the format, be sure to not include the meme format in any of the text. This meme will feature two text segments – one at the top and the other at the bottom. These two segments should be created by you and separated using the '|' symbol. The theme of the meme is '%s'. Maintain a light-hearted and humorous tone throughout. Please note, avoid using explicit labels like 'top text' or 'bottom text', and refrain from using quotation marks!"
PROMPT_NO_INPUT = "You are tasked with crafting a funny meme, using the %s meme format. Note that the meme should not be about the subject matter of the format, be sure to not include the meme format in any of the text. This meme will feature two text segments – one at the top and the other at the bottom. These two segments should be created by you and separated using the '|' symbol. Your task is to decide the theme and content of the meme. Maintain a light-hearted and humorous tone throughout. Please note, avoid using explicit labels like 'top text' or 'bottom text', and refrain from using quotation marks!"

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

def generate_meme_text(user_input, description):
    # Set the prompt based on whether user input was provided
    prompt = PROMPT % (description, user_input) if user_input else PROMPT_NO_INPUT % description

    # Generate meme phrase using GPT-4
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.8,
        max_tokens=150
    )

    # Choose "best" meme option
    return response['choices'][0]['text'].strip().split('\n')[0]

def generate_meme_image(template_id, meme_phrase):
    # Create meme using Imgflip API
    url = "https://api.imgflip.com/caption_image"
    meme_phrases = meme_phrase.split('|')
    params = {
        'template_id': str(template_id),  # ID of the meme template 
        'username': Config.IMGFLIP_USERNAME,
        'password': Config.IMGFLIP_PASSWORD,
        'font': "impact",
    }

    # Add texts dynamically (no longer useful after determining imgflip API only supports 2 text boxes)
    for i, phrase in enumerate(meme_phrases):
        params[f'text{i}'] = phrase
    res = requests.post(url, params)
    return json.loads(res.text)['data']['url']