from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from selenium.common.exceptions import TimeoutException
import concurrent.futures
import redis


class WebpageLinkCounter:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(8)

    def hyperlink_number(self, url):
        # cache, return if exist.
        cached_dynamic = self.redis.get(f"dynamic:{url}")
        cached_static = self.redis.get(f"static:{url}")

        if cached_dynamic and cached_static:
            print("Cached: Hyperlink")
            return max(int(cached_dynamic), int(cached_static))


        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_static = executor.submit(self.count_hyperlinks_static, url)
            future_dynamic = executor.submit(self.count_hyperlinks_dynamic, url)

            hyperlink_static = future_static.result()
            hyperlink_dynamic = future_dynamic.result()

            # write to cache
            print("count_hyperlinks_static", hyperlink_static)
            print("count_hyperlinks_dynamic", hyperlink_dynamic)
            self.redis.set(f"dynamic:{url}", hyperlink_dynamic, ex=604800)
            self.redis.set(f"static:{url}", hyperlink_static, ex=604800)
            return max(hyperlink_dynamic, hyperlink_static)

    # Method 1:
    # selenium dynamic link
    def count_hyperlinks_dynamic(self, url):
        try:
            try:
                self.driver.get(url)
            except TimeoutException:
                print("Page load timed out for URL:", url)
                return 0

            hyperlinks = self.driver.find_elements(By.TAG_NAME, "a")
            count = len(hyperlinks)
            return count

        except Exception as e:
            print(f"Error for URL {url}: {e}")
            return 0


    # Method 2:
    # static <a>
    def count_hyperlinks_static(self, url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            hyperlinks = soup.find_all('a')
            count = len(hyperlinks)
            return count
        except requests.RequestException as e:
            print(f"count_hyperlinks Error: {e}")
            return 0

    def close_browser(self):
        self.driver.quit()