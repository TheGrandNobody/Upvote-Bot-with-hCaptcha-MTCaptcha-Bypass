import csv
import random
import string
import proxy
import requests as req
import undetected_chromedriver as uc
from time import sleep
from mtcaptcha import mtsolver
from anticaptchaofficial import hcaptchaproxyless
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element_attribute


class Upvote():
    """ Initializes an upvote bot capable of generating temporary emails,
    creating accounts on coinsniper.net
    and upvoting a given token, 'n' amount of times. Saves all created accounts to a ".csv"
    """

    def __init__(self, n: int, project_url: str, captcha_key : str, proxy_key : str) -> None:
        """ Initializes an Upvote Bot.

        Args:
            n (int): The number of times which the upvote bot is required to vote
            project_url (str): The Coinsniper url of the project to be upvoted
            captcha_key (str): The API key for Anti-Captcha services
            proxy_key (str): The API key for the Webshare Proxy service
        """
        # Initialize Anti-Captcha solvers
        self.mt_solver = mtsolver()
        self.mt_solver.set_verbose(1)
        self.mt_solver.set_key(captcha_key)
        self.h_solver = hcaptchaproxyless.hCaptchaProxyless()
        self.h_solver.set_verbose(1)
        self.h_solver.set_key(captcha_key)
        self.h_solver.set_website_url(project_url)
        self.h_solver.set_website_key("65cdfa64-8ed6-49f2-a8ba-f4fc8501e917")
        self.h_solver.set_is_invisible(0)
        # Fetch a list of SOCKS5 proxies
        self.proxies = proxy.get_proxies(proxy_key)
        # Initialize other variables
        self.name = None
        self.password = None
        self.email = None
        self.token = None
        self.project_url = project_url
        self.votes = n
        self.proxy = 0
        # Initialize an Undetected Chrome driver with a SOCKS5 proxy
        self.setup(0)

    def __del__(self):
        self.driver.quit()

    def setup(self, i: int) -> None:
        """ Initializes an Undetected Chrome driver using a SOCKS5 proxy.

        Args:
            i (int): The index of the i'th proxy we want to use from the downloaded proxy list
        """
        options = uc.ChromeOptions()
        # Use a SOCKS5 proxy
        options.add_argument('--proxy-server=socks5://%s' % self.proxies[i])
        # Initialize Selenium Web Driver
        self.driver = uc.Chrome(options)
        self.h_solver.set_user_agent(self.driver.execute_script("return navigator.userAgent"))

    def restart(self) -> None:
        """ Closes the current Selenium web driver and reopens a new one with a new SOCKS5 proxy.
        """
        self.driver.quit()
        # Use the next proxy in the list if that is possible
        if self.proxy < len(self.proxies) - 1:
            self.proxy += 1
        # Otherwise go back to the beginning of the proxy list
        else:
            self.proxy = 0
        self.setup(self.proxy)

    def check_status_code(self, response) -> bool:
        """ Verifies that an HTTP request response has a successful status code.

        Args:
            response (Response): A response object

        Returns:
            bool: True if the status code lies between the range of 200 - 204, False otherwise
        """
        return 200 <= response.status_code <= 204

    def random_name(self) -> str:
        """ Generates a random, patternless user name that is difficult to track by websites.
        Uses a list of the 1000 most used words in the English language and random digits.
        Has a 50% chance of using two words from the list instead of one.

        Returns:
            str: A random patternless, hard-to-track user name
        """
        with open('names.txt', 'r') as file:
            names = file.readlines()
            self.name = names[random.randint(0, 999)][:-1] + (names[random.randint(
                0, 999)][:-1] if random.randint(0, 1) else '') + str(random.randint(0, 9999))
            return self.name

    def random_password(self) -> int:
        """ Generates a random, patternless password that is difficult to track by websites.
        The password is made of uppercase/lowercase letters, punctuation marks and numbers.
        It has a varying length of 12-16 characters.

        Returns:
            int: A random patternless, hard-to-track password
        """
        self.password = ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation, k=random.randint(12, 16)))
        return self.password

    def random_email(self) -> str:
        """ Generates a temporary email address which the bot can use to register/verify an account on a website.

        Raises:
            Exception: Thrown if the bot failed to fetch a temporary email domain using a GET request
            Exception: Thrown if the bot failed to create a temporary email account using a POST request
            Exception: Thrown if the bot failed to obtain an authorization token using a POST request

        Returns:
            str: A temporary email address
        """
        try:
            # Try fetching a temporary email domain
            response = req.get('https://api.mail.tm/domains?page=1')
            if self.check_status_code(response):
                # Create an email address using the acquired domain
                content = response.json()
                self.email = self.name+'@'+content['hydra:member'][0]['domain']
                # Create a temporary mail account using the newly created email
                response = req.post(
                    'https://api.mail.tm/accounts', json={'address': self.email, 'password': self.password})
                if self.check_status_code(response):
                    # Fetch an authentication token using the newly created account
                    response = req.post(
                        'https://api.mail.tm/token', json={'address': self.email, 'password': self.password})
                    if self.check_status_code(response):
                        # Save the authentication token
                        content = response.json()
                        self.token = 'Bearer ' + content['token']
                    else:
                        raise Exception(
                            'Error while fetching POST response to get token with status code: ' + str(response.status_code))
                else:
                    raise Exception(
                        'Error while fetching POST response to create account with status code: ' + str(response.status_code))
            else:
                raise Exception(
                    'Error while fetching GET response to get email domains, with status code: ' + str(response.status_code))
        except Exception as error:
            print(error)
        return self.email

    def fetch_verification_link(self) -> str:
        """ Searches the temporary email address' messages to find the Coinsniper account verification link.

                Raises:
                        Exception: Thrown if the bot failed to fetch its temporary email address' inbox contents in a GET request
                        Exception: Thrown if the bot failed to specifically fetch the verification email in a GET request

                Returns:
                        str: The URL used to verify the Coinsniper account
                """
        try:
            # Try to fetch all emails stored in the temporary email account
            response = req.get('https://api.mail.tm/messages?page=1',
                               headers={'Authorization': self.token})
            if self.check_status_code(response):
                # Check whether any emails have been received
                content = response.json()
                # Keep fetching the temporary email account's inbox until we receive the verification email
                while content['hydra:totalItems'] == 0:
                    print('Waiting for verification email. Please be patient')
                    sleep(5)
                    response = req.get(
                        'https://api.mail.tm/messages?page=1', headers={'Authorization': self.token})
                    content = response.json()
                print('Verification email arrived')
                # Save the ID of the verification email once it has been received
                id = content['hydra:member'][0]['@id']
                # Try to fetch the contents of the verification email
                response = req.get('https://api.mail.tm' +
                                   id, headers={'Authorization': self.token})
                if self.check_status_code(response):
                    # Search the email's contents for the verification link
                    content = response.json()
                    verification_link = content['text'].splitlines()[6][22:]
                else:
                    raise Exception(
                        'Error while fetching GET response to get verification email, with status code: ' + str(response.status_code))
            else:
                raise Exception(
                    'Error while fetching GET response to get emails, with status code: ' + str(response.status_code))
        except Exception as error:
            print(error)
        print("Obtained a verification link")
        return verification_link

    def register_and_verify(self) -> None:
        """ Creates an account on Coinsniper and automatically verifies it.
        """
        print('Creating an account...')
        # 1 | Open https://coinsniper.net/register |
        self.driver.get('https://coinsniper.net/register')
        # 2 | Try closing the ad
        try:
            WebDriverWait(self.driver, 10).until(text_to_be_present_in_element_attribute((By.CLASS_NAME, "premium-banner"), "class", "is-open"))
            self.driver.find_element(By.CSS_SELECTOR, ".fa-times-circle").click()
        except:
            pass
        # 3 | Try closing the disclaimer
        try:
            self.driver.find_element(By.CSS_SELECTOR, ".full-width").click()
        except:
            pass
        # 4 | Click on the name field
        try:
            self.driver.find_element(By.NAME, "name").click()
        except:
            pass
        # 5 | Type a random name
        try:
            self.driver.find_element(By.NAME, "name").send_keys(self.random_name())
        except:
            pass
        # 6 | Click on the password field
        try:
            self.driver.find_element(By.NAME, "password").click()
        except:
            pass
        # 7 | Type a random password
        try:
            self.driver.find_element(By.NAME, "password").send_keys(self.random_password())
        except:
            pass
        # 8 | Click on the password confirmation field
        try:
            self.driver.find_element(By.NAME, "password_confirmation").click()
        except:
            pass
        # 9 | Re-enter the previously generated password
        try:
            self.driver.find_element(
                By.NAME, "password_confirmation").send_keys(self.password)
        except:
            pass
        # 10 | Click on the email field
        try:
            self.driver.find_element(By.NAME, "email").click()
        except:
            pass
        # 11 | Type a temporary email address
        try:
            self.driver.find_element(
                By.NAME, "email").send_keys(self.random_email())
        except:
            pass
        # 12 | Switch to the MTCaptcha frame
        print('Attempting to solve MTCaptcha...')
        try:
            self.driver.switch_to.frame(self.driver.find_element(By.ID, "mtcaptcha-iframe-1"))
        except:
            pass
        # 13 | Keep trying to solve the captcha until successful
        self.solve_mt_captcha()
        # 14 | Switch back to the (default) website registration frame
        try:
            self.driver.switch_to.default_content()
        except:
            pass
        sleep(1)
        # 15 | Click on "Register"
        try:
            self.driver.find_element(By.CSS_SELECTOR, "body > section.register > div > div > div > div > form").submit()
        except:
            pass
        print('Account created, beginning verification process...')
        # 16 | Verify the newly created account
        try:
            self.driver.get(self.fetch_verification_link())
        except:
            pass

    def solve_mt_captcha(self) -> None:
        """ Attempts to solve an MTCaptcha continuously, until it is solved.
        """
        # 1 | Save the captcha's image url
        try:
            base64_captcha_image = self.driver.find_element(
                By.ID, "mtcap-image-nocss-1").get_attribute("src")
        except:
            pass
        # 2 | Send the image to anti-captcha for solving
        solution = self.mt_solver.solve_and_return_solution(base64_captcha_image[22:])
        # 3 | Click on the MTCaptcha input field
        try:
            self.driver.find_element(By.ID, "mtcap-inputtext-1").click()
        except:
            pass
        # 4 | Enter the solved MTCaptcha key
        try:
            self.driver.find_element(By.ID, "mtcap-inputtext-1").send_keys(solution)
        except:
            pass
        # 5a | Wait max 5s for the captcha to verify
        try:
            WebDriverWait(self.driver, 5).until(text_to_be_present_in_element_attribute((By.ID, "desc4InputText-1"), "innerHTML", "captcha verified successfully."))
        except:
        # 5b | Otherwise attempt to solve the captcha again
            # If connection timed out, reset the captcha
            if "block" in self.driver.find_element(By.ID, "mtcap-error-card-1").get_property("display"):
                try:
                    self.driver.find_element(By.ID, "mtcap-alert-btn-1").click()
                except:
                    pass
                sleep(1)
            self.solve_mt_captcha()

    def vote(self) -> None:
        """ Upvotes the given project on Coinsniper and adds it to the account's watchlist.
        """
        print('Beginning voting procedure...')
        # 1 | Open the project on Coinsniper
        try:
            self.driver.get(self.project_url)
        except:
            pass
        # 2 | Try closing the ad
        try:
            WebDriverWait(self.driver, 10).until(text_to_be_present_in_element_attribute((By.CLASS_NAME, "premium-banner"), "class", "is-open"))
            self.driver.find_element(By.CSS_SELECTOR, ".fa-times-circle").click()
        except:
            pass
        # 3 | Try closing the disclaimer
        try:
            self.driver.find_element(By.CSS_SELECTOR, ".full-width").click()
        except:
            pass
        # 4 | 33% Chance to add the project to your watchlist
        if (not random.randint(0, 2)):
            print("Adding project to this account's watchlist.")
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, ".wishlist-add > span").click()
            except:
                pass
        else:
            print('Account will not add this project to the watchlist.')
        # 5 | Click on the "Vote For [Project]" button
        try:
            self.driver.find_element(
                By.CSS_SELECTOR, ".is-hidden-mobile > .voting > .button").click()
        except:
            pass
        sleep(5)
        # 6 | Solve the captcha
        print('Attempting to solve hCaptcha challenge...')
        solution = self.h_solver.solve_and_return_solution()
        # 7 | Enter the hCaptcha response 
        try:
            self.driver.execute_script("arguments[0].value = '{}'".format(solution), self.driver.find_element(By.NAME, 'h-captcha-response'))
        except:
            pass
        try:
            self.driver.execute_script("arguments[0].value = '{}'".format(solution), self.driver.find_element(By.NAME, 'g-recaptcha-response'))
        except:
            pass
        # 8 | Click on the hCaptcha checkbox
        try:
            self.driver.find_element(By.ID, "hcaptcha_submit").submit()
        except:
            pass
        sleep(5)

    def save_credentials(self):
        """ Saves the email and password of the current newly created Coinsniper account to a '.csv' file.
        """
        with open('coinsniper_accounts.csv', 'a') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([self.email, self.password])

    def activate(self) -> None:
        """ Activates the bot's upvoting procedure.
        """
        for i in range(self.votes):
            # 1 | Register and verify a Coinsniper account
            self.register_and_verify()
            # 2 | Upvote the given project and adds it to the new account's watchlist
            self.vote()
            print('Voted. %d votes left' % (self.votes - (i + 1)))
            # 3 | Save the account's credentials to a '.csv' file
            self.save_credentials()
            # 4 | Repeat 1-3 for the number of specified times
            if i < self.votes - 1:
                self.restart()
            else:
                self.driver.quit()
