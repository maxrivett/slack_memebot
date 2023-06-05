from dotenv import load_dotenv
import os
import openai
from slack_sdk import WebClient

class Config:
    IMGFLIP_USERNAME = None
    IMGFLIP_PASSWORD = None
    client = None

    @staticmethod
    def load_env_variables():
        load_dotenv()
        openai.api_key = os.getenv("API_KEY")
        slack_token = os.getenv("SLACK_TOKEN")
        Config.client = WebClient(token=slack_token)
        Config.IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
        Config.IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")