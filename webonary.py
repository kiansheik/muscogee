import os
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.webonary.org/muscogee/browse/browse-muscogee/"
local_folder = "dict_html/"


def save_html(url, page_number, letter):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure we have a valid response

        # Save the HTML content to a file
        filename = f"{local_folder}/{letter}_page_{page_number}.html"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"Saved {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")


def find_and_follow(url, selector, letter):
    page_number = 1
    while True:
        filename = f"{local_folder}/{letter}_page_{page_number}.html"
        # If the filename already exists, skip this page
        if os.path.exists(filename):
            print(f"Skipping page {page_number} for letter {letter}. Already saved.")
            # get file as string
            with open(filename, "r", encoding="utf-8") as file:
                html = file.read()
            soup = BeautifulSoup(html, "html.parser")
        else:
            # Send a GET request to the URL
            time.sleep(2)  # Be respectful to the website, avoid being too fast
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve {url}. Status code: {response.status_code}")
                break

            # Parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")

        # Save the current page's HTML
        save_html(url, page_number, letter)

        # Find the next page link
        next_page = soup.select_one(selector)

        if next_page and "active_page" in next_page.get("class", []):
            print("Reached the final page.")
            break
        elif next_page:
            # Get the next page URL from the <a> tag
            next_link = next_page.find("a", href=True)
            if next_link:
                url = BASE_URL + next_link["href"]
                # Make sure the link is absolute, if it's relative
                if not url.startswith("http"):
                    url = requests.compat.urljoin(url, url)
                page_number += 1
            else:
                print("Next page link not found.")
                break
        else:
            print(f"Selector '{selector}' not found on page {page_number}. Stopping.")
            break


letters = "a c e f h i k l m n o p r s t u v w y".split(" ")

# Example usage
for letter in letters:
    start_url = BASE_URL + f"?key=mus&letter={letter}"
    selector = "#wp_page_numbers > ul > li:nth-last-child(1)"
    find_and_follow(start_url, selector, letter)
