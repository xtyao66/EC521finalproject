from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import concurrent.futures

def hyperlink_number(url):
    hyperlink_static = count_hyperlinks_static(url)
    hyperlink_dynamic = -1
    # Execute count_hyperlinks_dynamic with a timeout
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(count_hyperlinks_dynamic, url)
        try:
            # Wait for 5 seconds for count_hyperlinks_dynamic to complete
            hyperlink_dynamic = future.result(timeout=15)
        except concurrent.futures.TimeoutError:
            print("count_hyperlinks_dynamic timed out. Continuing with static count.")

    return max(hyperlink_dynamic, hyperlink_static)


# Method 1:
# Chrome Dynamic
def count_hyperlinks_dynamic(url):
    try:
        driver = webdriver.Chrome()
        driver.get(url)

        time.sleep(2)

        hyperlinks = driver.find_elements(By.TAG_NAME, "a")
        count = len(hyperlinks)

        driver.quit()
        print("count_hyperlinks_dynamic", count)
        return count
    except Exception as e:
        print(f"Error: {e}")
        return -1


# Method 2:
# static <a>
def count_hyperlinks_static(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        hyperlinks = soup.find_all('a')
        count = len(hyperlinks)
        print("count_hyperlinks_static", count)
        return count
    except requests.RequestException as e:
        print(f"count_hyperlinks Error: {e}")
        return -1

# UT
def hyperlinks_ut():
    url = "https://www.reddit.com/?rdt=47356"
    print(url)
    count_hyperlinks_dynamic(url)
    count_hyperlinks_static(url)
    