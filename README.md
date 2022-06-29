# Upvote bot with hCaptcha/MTCaptcha Bypass
This bot creates accounts using a temporary email address and automatically verifies them to then vote for a given project on Coinsniper.net. It generates about one vote per minute. 

# How to use the bot
Download the repository and open the main.py file. Enter the amount of votes (VOTES_PER_BOT) you want your bot to perform in consecution, the coinsniper.net page (PROJECT_URL) of your token (it is set to SHEBA Token by default), your Anti-Captcha API key (CAPTCHA_KEY) and your Proxy Webshare API key (PROXY_KEY). 

Once you have filled these four strings of information, you must open terminal, navigate to this folder and install dependencies:
```
pip install -r requirements.txt
```

Then, simply begin the script by typing:
```
python3 main.py
```
