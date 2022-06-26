import threading
import csv
from os.path import exists
from upvote import Upvote 

NUMBER_OF_BOTS = 1  # The number of bots you want to run in parallel
VOTES_PER_BOT = 1  # The number of votes/accounts created per bot
PROJECT_URL = 'https://coinsniper.net/coin/27477' # The Coinsniper URL of the project you want to upvote

lock = threading.Lock() # A lock used to make sure each bot does not compete to write into the csv files

if __name__ == "__main__":
    if not exists('coinsniper_accounts.csv'):
        with open('coinsniper_accounts.csv', 'w') as file:
            writer = csv.writer(file, delimiter=',')
            header = writer.writerow(['Email', 'Password'])
    bots = [Upvote(VOTES_PER_BOT, PROJECT_URL) for _ in range(NUMBER_OF_BOTS)]
    # Run the bots in parallel
    threads = []
    for bot in bots:
      thread = threading.Thread(bot.activate)
      threads.append(thread)
      thread.start()
    # Wait for the threads to complete their process
    for thread in threads:
      thread.join()
        