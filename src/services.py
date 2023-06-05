from config import Config
from slack_sdk.errors import SlackApiError
from utils import get_random_template_id, generate_meme_text, generate_meme_image

def post_meme_in_chat(user_input, user_id, channel_id):
    # Send the "Creating your meme now..." message
    response = Config.client.chat_postMessage(
        channel=channel_id,
        text='Creating your meme now...'
    )
    
    username = ''
    # Get the user's username using the Slack API
    try:
        user_info = Config.client.users_info(user=user_id)
        username = user_info['user']['name']
    except SlackApiError as e:
        username = 'Unknown User'
    
    # Get the 'ts' of the message we just sent
    ts = response['ts']

    template_id, description = get_random_template_id()
    meme_phrase = generate_meme_text(user_input, description)
    meme_url = generate_meme_image(template_id, meme_phrase)
    
    # Delete the "Creating your meme now..." message
    Config.client.chat_delete(
        channel=channel_id,
        ts=ts
    )

    # Post meme to Slack channel
    Config.client.chat_postMessage(
        channel=channel_id,
        text=f"Here's your meme about {user_input}, {username}:" if user_input else f"Here's your meme, {username}:",
        attachments=[{"image_url": meme_url, "author_name": "_", "author_link": "https://www.maxrivett.com"}]
    )