# slack_memebot

After a professor in one of my classes suggested (in a Slack channel) that a Slack-command-called meme generator powered by GPT would be funny, I took it upon my bored self to create it.

Note that the memes generated tend to be rather unfunny given the cold nature of GPT 3.5, but at times this makes them funnier.

## Getting Started

In order to run the meme generator, I did the following:

- Created a Slack app with a slash command using the Slack API
- Created an `ngrok` tunnel using `ngrok http 5000` and used the provided URL as the Slack app Requests URL
- Added the Slack app to a Slack channel and ran it with `/creatememe` to see the magic happen
