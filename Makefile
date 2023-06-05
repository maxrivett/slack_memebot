SHELL := /bin/bash

run-ngrok:
	@echo "Starting ngrok..."
	ngrok http 5000 &

run-app:
	@echo "Starting the Flask app..."
	cd src && python3 main.py &

start: run-ngrok run-app
	@echo "ngrok and Flask app are running."
	@echo "Please open http://127.0.0.1:4040 to find your ngrok URL and update your Slack slash command with <ngrok_url>/meme-endpoint"