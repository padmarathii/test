import csv
import socket
import ssl
import whois
from datetime import datetime

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

import requests

from bs4 import BeautifulSoup
# from dateutil.relativedelta import relativedelta

import time

print("Started writing to CSV file...")
start_time = time.time()

# Define a list of blacklisted words
blacklist = [
    'spam', 'scam', 'fraud', 'phishing', 'gift', 'surprise', 'real', 'legit',
    'trusted', 'seller', 'buyer', 'fast'
]

# Define a list of file extensions to check for
file_extensions = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar',
    '.apk', '.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.tar.gz',
    '.tar.bz2', '.tar.xz', '.tar', '.zipx', '.7z', '.rar', '.gz', '.bz2', '.xz',
    '.z', '.lzma', '.lz', '.lzo', '.wim', '.swm', '.esd', '.cab', '.arj', '.chm',
    '.cramfs', '.dmg', '.fat', '.hfs', '.iso', '.lzh', '.lzma', '.mbr', '.msi',
    '.nsis', '.ntfs', '.qcow2', '.rpm', '.squashfs', '.udf', '.vhd', '.vmdk',
    '.xar', '.z', '.zip', '.zipx', '.zoo', '.zpaq', '.zst', '.tar', '.tar.gz',
    '.tar.bz2', '.tar.xz', '.tar.lzma', '.tar.lz', '.tar.lzo', '.tar.zst',
    '.tar.z', '.tar.Z', '.tar.lz4', '.tar.sz', 'exe'
]

# Open the input CSV file for reading
with open('input.csv', mode='r') as csv_file:
    # Create a CSV reader object
    csv_reader = csv.reader(csv_file)

    # Create a list to store the output data
    output_data = []

    # Create a new WebDriver object
    # driver = webdriver.Chrome()

    # Loop through each row in the input CSV file
    for row in csv_reader:

        # Extract the URL from the row
        url = row[0]
        print(url)

        # Get the IP address of the URL
        try:
            ip_address = socket.gethostbyname(url)
        except:
            ip_address = ""
        print(ip_address)
        if ip_address != "":
            # Check if SSL is present for the URL
            try:
                context = ssl.create_default_context()
                with socket.create_connection((url, 443)) as sock:
                    with context.wrap_socket(sock, server_hostname=url) as ssock:
                        ssl_present = True
            except:
                ssl_present = False

            # Check the age of the website

            try:

                domain = whois.whois(url)

                if isinstance(domain.creation_date, list):

                    delta = datetime.now() - domain.creation_date[0]
                    age = delta.days

                    # delta = relativedelta(datetime.now(), domain.creation_date[0])
                    # print(delta)
                    # years = delta.years
                    # months = delta.months
                    # days = delta.days

                    # age =str(years) + " years, "+ str(months) + " months, " + str(days) + " days"
                else:

                    delta = datetime.now() - domain.creation_date
                    age = delta.days

                    # delta = relativedelta(datetime.now(), domain.creation_date)
                    # years = delta.years
                    # months = delta.months
                    # days = delta.days

                    # age =str(years) + " years "+ str(months) + " months, " + str(days) + " days"

            except:
                age = ""

            # Navigate to the URL with the WebDriver
            # driver.get(url)

            # Wait for up to 10 seconds for any element with the class "modal" to appear
            # try:
            #     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modal")))
            #     popups_present = True
            # except:
            #     popups_present = False

            # Send a GET request to the URL and get its HTML content

            # Redirects
            # import dns.resolver
            # answers = dns.resolver.resolve(url, 'A')
            # ip_address = answers[0].address
            # print(ip_address)

            try:
                ip_address = socket.gethostbyname(url)
                if url[:4] != 'http':
                    http_url = 'http://www.' + url
                    https_url = 'https://www.' + url
                    response = requests.get(https_url)
                    if response.status_code == 200:
                        url = https_url
                    else:
                        url = http_url

                response = requests.get(url, allow_redirects=True)
                print(url)
                num_redirects = len(response.history)

                status_code = response.status_code



            except:
                num_redirects = ''
                print(url)
                try:

                    url = 'https://www.' + url
                    print(url)
                    response = requests.get(url)
                    # hashedprint(response)
                    status_code = response.status_code
                except:
                    status_code = ''

            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                payment_options = []
                for form in soup.find_all('form'):

                    # hashedprint(form)

                    if 'payment' in str(form).lower() or 'checkout' in str(form).lower():
                        print('h')
                        payment_options.append(form.get('action'))
                webpage_text = response.text.lower()
                blacklisted_words = [word for word in blacklist if word in webpage_text]
                webpage_text = response.text
                downloadable_links = []
                for extension in file_extensions:
                    links_with_extension = [
                        link.get('href')
                        for link in BeautifulSoup(webpage_text, 'html.parser').find_all('a')
                        if link.get('href').endswith(extension)
                    ]
                    downloadable_links.extend(links_with_extension)


            except:

                payment_options = ""
                blacklisted_words = ""
                downloadable_links = ""
                soup = None

            # Find all links on the page and check if they are broken
            if soup is not None:
                links = soup.find_all('a')
                for link in links:
                    href = link.get('href')
                    if href is not None and not href.startswith('#'):
                        try:
                            link_response = requests.get(href)
                            link_status_code = link_response.status_code
                            if link_status_code >= 400:
                                print(f"Broken link found on {url}: {href}")
                        except:
                            pass

            # Find all buttons on the page and check if they are functional
            if soup is not None:
                buttons = soup.find_all('button')
                for button in buttons:
                    onclick = button.get('onclick')
                    if onclick is not None:
                        try:
                            eval(onclick)
                        except:
                            # Non-functional button found
                            print(f"Non-functional button found on {url}: {onclick}")

            # Add the IP address, SSL information, and age to the output data list
            output_data.append([
                ip_address, ssl_present, age, num_redirects, status_code,
                payment_options, blacklisted_words, downloadable_links
            ])

    # Open the output CSV file for writing
    with open('output.csv', mode='w', newline='') as csv_file:

        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        # Write the header row
        csv_writer.writerow([
            'ip', 'ssl', 'age', 'redirects', 'status_code', 'payment_options',
            'blacklisted_words', 'downloadable_links'
        ])  # re

        # Write the output data
        csv_writer.writerows(output_data)
    print("Finished writing to CSV file...")

    # Close the WebDriver
    # driver.quit()
    # End Time
    end_time = time.time()
    
    # Calculate the time required to run the code
    elapsed_time = end_time - start_time

    # Display the time in seconds
    print(f"Elapsed time: {elapsed_time:.6f} seconds")
