#pip install bs4 pythondns dnspython Levenshtein requests tqdm python-whois urllib3

from bs4 import BeautifulSoup
import csv
from datetime import datetime
import dns.resolver
import heapq
import Levenshtein
import requests
import threading
import time
import ssl
import subprocess
import whois
import urllib3


urllib3.disable_warnings()

print("Started writing to CSV file...")

# Define a list of blacklisted words
blacklist = [
    'spam', 'scam', 'fraud', 'phishing', 'gift', 'surprise', 'real', 'legit', 'trusted', 'seller', 'buyer', 'fast', 'secure', 'login', 'verify', 'account', 'update', 'confirm', 'bank', 'paypal', 'ebay', 'amazon', 'ebay', 'apple', 'microsoft', 'google', 'facebook', 'instagram', 'twitter', 'snapchat', 'linkedin', 'youtube', 'whatsapp', 'gmail', 'yahoo', 'outlook', 'hotmail', 'aol', 'icloud', 'instant' 'bitcoin', 'litecoin', 'ethereum', 'dogecoin', 'binance', 'coinbase', 'coinmarketcap', 'cryptocurrency', 'cryptocurrencies', 'crypto', 'currency', 'blockchain', 'btc', 'eth', 'ltc', 'doge', 'bch', 'xrp', 'xlm', 'ada', 'usdt', 'usdc', 'dai', 'wbtc', 'uniswap', 'sushiswap', 'pancakeswap', 'defi', 'decentralized', 'finance', 'defi', 'yield', 'farming', 'staking', 'staking', 'pool', 'pooling', 'staking', 'staking', 'staking', 'join', 'group', 'telegram', 'whatsapp', 'discord', 'discord nitro', 'antivirus'
]

# Open the input CSV file for reading

with open('input.csv', mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    output_data = []
    threads = []
    reader = csv.reader(csv_file)



# Define a function to process each URL in a separate thread

    def process_url(url):

        # # Get the IP address of the URL
        # try:
        #     ip_address = requests.get(f'http://ip-api.com/json/{url}').json().get('query')
        # except:
        #     ip_address = ''

        start_time = time.time()

        # Length of the URL

        try:
            length_url = len(url)

        except:
            length_url = ''

        # Check if SSL is present for the URL

        try:
            context = ssl.create_default_context()
            with requests.get(f'https://{url}', verify=False, timeout=5) as response:
                ssl_present = response.ok
        except:
            ssl_present = False

        # Get the age of the domain in days

        try:
            domain = whois.whois(url)
            if isinstance(domain.creation_date, list):
                delta = datetime.now() - domain.creation_date[0]
                age = delta.days
            else:
                delta = datetime.now() - domain.creation_date
                age = delta.days
        except:
            age = ''

        # Check for the nameserver of the website

        try:

            domain = url#[4:]
            answers = dns.resolver.resolve(domain, 'NS')
            nsdata = []
            for rdata in answers:
                data = rdata.to_text()
                nsdata.append(data[:-1])
            output_list = [line.strip() for line in nsdata]

            output_str = ''
            for i in range(len(output_list)):
                if i == 0:
                    output_str += output_list[i]
                else:
                    output_str += ', ' + output_list[i]
            nameservers = '[' + output_str + ']'

        except:

            nameservers = ''

        # Get the status code of the website

        try:
            response = requests.get(f'https://{url}', verify=False, timeout=5)
            if response.status_code != 200:
                response = requests.get(f'http://{url}', verify=False, timeout=5)
            status_code = response.status_code
        except:
            status_code = ''

        # Check for iframes in the website

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            iframes = soup.find_all('iframe')

        except:
            iframes = '0'

        # Check for blacklisted words in the website

        try:
            webpage_text = response.text
            blacklisted_words = [word for word in blacklist if word in webpage_text]

        except:
            blacklisted_words = ''

        # Get the number of blacklisted words being found

        try:
            len_of_blacklisted_words = len(blacklisted_words)

        except:
            len_of_blacklisted_words = ''

        # Get the time taken to process everything so far

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(url)

        # Get the most similar website(not working because files are not present)

        try:
            target = url[4:]
            first_char = target[0].lower()
            filename = f"{first_char}.txt"

            with open(filename) as f:
                strings = {line.rstrip() for line in f}

            # Calculate Levenshtein distance for all strings and get top 3
            top_3_strings = heapq.nsmallest(3, strings, key=lambda x: Levenshtein.distance(target, x))

            for i, s in enumerate(top_3_strings):
                print()

            # Save top 3 most similar strings in a variable
            similar = list(top_3_strings)
            print(similar)

        except:
            similar = ''

        # Add the SSL information, Age, Status Code, Nameservers, Blacklisted Words, Total Blacklisted Words and Time to the output data list

        output_data.append({
            'url': url,
            'length_url': length_url,
            'ssl': ssl_present,
            'age': age,
            'status_code': status_code,
            'iframes': iframes,
            'blacklisted_words': blacklisted_words,
            'elapsed_time': elapsed_time,
            'nameservers': nameservers,
            'len_of_blacklisted_words': len_of_blacklisted_words,
            'similar': similar
        })


    # Loop through each row in the input CSV file

    for row in csv_reader:
        # Extract the URL from the row
        url = row[0]
        # Create a new thread to process the URL
        thread = threading.Thread(target=process_url, args=(url,))
        threads.append(thread)
        # Start the thread
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

# Open the output CSV file for writing
with open('output.csv', mode='w', newline='') as csv_file:

    # Create a CSV writer object

    fieldnames = ['url', 'length_url', 'ssl', 'age', 'status_code', 'iframes', 'blacklisted_words', 'elapsed_time', 'nameservers', 'len_of_blacklisted_words','similar']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write the header row
    csv_writer.writeheader()

    # Write the output
    csv_writer.writerows(output_data)

print("Finished writing to CSV file...")
