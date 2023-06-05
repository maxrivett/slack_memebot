from flask import Flask, request
from config import Config
from services import post_meme_in_chat
import threading

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
Config.load_env_variables()

@app.route('/meme-endpoint', methods=['POST'])
def create_meme():
    # Parse the request payload
    payload = request.form

    # Extract the user input from the payload
    user_input = payload['text']
    channel_id = payload['channel_id']
    user_id = payload['user_id']

    threading.Thread(target=post_meme_in_chat, args=(user_input, user_id, channel_id)).start()

    return '', 200  # Empty response, status code 200

# Start the flask app
if __name__ == "__main__":
    app.run(debug=True)