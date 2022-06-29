import csv
from os.path import exists
from upvote import Upvote

VOTES_PER_BOT = 3  # The number of votes/accounts created per bot
PROJECT_URL = 'https://coinsniper.net/coin/27477' # The Coinsniper URL of the project you want to upvote
CAPTCHA_KEY = 'be72f71c3deac04756eda6c5b263c3a8' # The API key for your Anti-Captcha account
PROXY_KEY = 'db95f3f33e86ef6274fca26a09c975809b56c801' # The API key for your Proxy Webshare account

def main() -> None:
    # Check whether there is already a '.csv' file to append accounts to
    if not exists('coinsniper_accounts.csv'):
        # Otherwise create one and add a header to it
        with open('coinsniper_accounts.csv', 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Email', 'Password'])
    # Run the bot
    bot = Upvote(VOTES_PER_BOT, PROJECT_URL, CAPTCHA_KEY, PROXY_KEY)
    bot.activate()

if __name__ == "__main__":
    main()
