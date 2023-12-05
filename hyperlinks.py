from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from selenium.common.exceptions import TimeoutException

def hyperlink_number(url):
    hyperlink_static = count_hyperlinks_static(url)
    hyperlink_dynamic = count_hyperlinks_dynamic(url)
    return max(hyperlink_dynamic, hyperlink_static)


# Method 1:
# Chrome Dynamic
def count_hyperlinks_dynamic(url):
    try:
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(8) 

        try:
            driver.get(url)
        except TimeoutException:
            print("Page load timed out. Exiting.")
            return -1

        time.sleep(2)

        hyperlinks = driver.find_elements(By.TAG_NAME, "a")
        count = len(hyperlinks)

    except Exception as e:
        print(f"Error: {e}")
        return -1
    finally:
        driver.quit()  

    print("count_hyperlinks_dynamic", count)
    return count


# Method 2:
# static <a>
def count_hyperlinks_static(url):
    try:
        response = requests.get(url, timeout=3)
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
    