import csv
from os.path import exists
from upvote import Upvote
from concurrent.futures import ThreadPoolExecutor

NUMBER_OF_BOTS = 2 # The number of bots we create
VOTES_PER_BOT = 3  # The number of votes/accounts created per bot
PROJECT_URL = 'https://coinsniper.net/coin/27477' # The Coinsniper URL of the project you want to upvote
CAPTCHA_KEY = 'be72f71c3deac04756eda6c5b263c3a8' # The API key for your Anti-Captcha account
PROXY_KEY = 'db95f3f33e86ef6274fca26a09c975809b56c801' # The API key for your Proxy Webshare account
USERNAME = 'rabsuvcm' # The Proxy authentication username
PASSWORD = '6rwl67s21x3e' # The Proxy authentication password

def initiate(bot : Upvote, proxy_idx : int):
    # Run the bot
    bot.activate(proxy_idx)

def main() -> None:
    # Check whether there is already a '.csv' file to append accounts to
    if not exists('coinsniper_accounts.csv'):
        # Otherwise create one and add a header to it
        with open('coinsniper_accounts.csv', 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Email', 'Password'])
    with ThreadPoolExecutor(max_workers=NUMBER_OF_BOTS) as executor:
        executor.map(initiate, [Upvote(VOTES_PER_BOT, PROJECT_URL, CAPTCHA_KEY, PROXY_KEY, USERNAME, PASSWORD) for _ in range(NUMBER_OF_BOTS)], [i * VOTES_PER_BOT for i in range(NUMBER_OF_BOTS) ])

if __name__ == "__main__":
    main()
