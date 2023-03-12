import csv
import requests
import time
import ssl
import whois
import urllib3
from datetime import datetime
import threading

urllib3.disable_warnings()

print("Started writing to CSV file...")

# Define a list of blacklisted words
blacklist = [
    'spam', 'scam', 'fraud', 'phishing', 'gift', 'surprise', 'real', 'legit',
    'trusted', 'seller', 'buyer', 'fast'
]

# Open the input CSV file for reading
with open('input.csv', mode='r') as csv_file:
    # Create a CSV reader object
    csv_reader = csv.reader(csv_file)
    # Create a list to store the output data
    output_data = []
    # Create a list to store the threads
    threads = []

    # Define a function to process each URL in a separate thread
    def process_url(url):
        # Get the IP address of the URL
        try:
            ip_address = requests.get(f'http://ip-api.com/json/{url}').json().get('query')
        except:
            ip_address = ''

        # Check if SSL is present for the URL
        start_time = time.time()
        try:
            context = ssl.create_default_context()
            with requests.get(f'https://{url}', verify=False, timeout=5) as response:
                ssl_present = response.ok
        except:
            ssl_present = False

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

        try:
            response = requests.get(f'https://{url}', verify=False, timeout=5)
            if response.status_code != 200:
                response = requests.get(f'http://{url}', verify=False, timeout=5)
            status_code = response.status_code
        except:
            status_code = ''

        try:
            webpage_text = response.text.lower()
            blacklisted_words = [word for word in blacklist if word in webpage_text]
        except:
            blacklisted_words = ''

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Add the SSL information, Age, Status Code, Blacklisted Words and Time to the output data list
        output_data.append({
            'ssl': ssl_present,
            'age': age,
            'status_code': status_code,
            'blacklisted_words': blacklisted_words,
            'elapsed_time': elapsed_time
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
    fieldnames = ['ssl', 'age', 'status_code', 'blacklisted_words', 'elapsed_time']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write the header row
    csv_writer.writeheader()

    # Write the output
    csv_writer.writerows(output_data)
print("Finished writing to CSV file...")
