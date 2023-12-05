import requests
import urllib.parse as p
from utils import get_domain
from bs4 import BeautifulSoup

# Setup your search_engine_id and api_key refer to this
# https://developers.google.com/custom-search/v1/introduction
API_KEY = ""
SEARCH_ENGINE_ID = ""

# otherwise it will use request, ip could be baned
def index_serach(url):
    if API_KEY == "":
        return check_google_index_requests(url)
    else:
        return check_google_index_api(url)


# Method 1:
# Use custom google search engine API to check whether the subdomain is indexed.
# 0: indexed; 1: not indexed 
def check_google_index_api(url):
    # extract subdomain
    url = get_domain(url)
    query = f"site:{url}"
    page = 1
    start = (page - 1) * 10 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"

    data = requests.get(url).json()

    # return maximum 10 results from the start point.
    search_items = data.get("items")
    if search_items == None:
        print("site not indexed.")
        return 1
    else:
        for i, search_item in enumerate(search_items, start=1):
            title = search_item.get("title")
            snippet = search_item.get("snippet")
            #html_snippet = search_item.get("htmlSnippet")
            link = search_item.get("link")
            print("="*10, f"Result #{i+start-1}", "="*10)
            print("Title:", title)
            print("Description:", snippet)
            print("URL:", link, "\n")
        print("site indexed.")
        return 0


# Method2: 
# Use Chrome Driver
# 0: indexed; 1: not indexed 
def check_google_index_chrome(url):
    url = get_domain(url)
    driver = webdriver.Chrome()

    driver.get("https://www.google.com")

    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(f"site:{url}")
    search_box.send_keys(Keys.RETURN)

    time.sleep(3) 

    results = driver.find_elements(By.XPATH, "//div[@id='search']//a")
    indexed = any(url in result.get_attribute('href') for result in results)

    driver.quit()

    return indexed

# Method3:
# request google search directly, ip will be baned.
def check_google_index_requests(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    try:
        response = requests.get(f"https://www.google.com/search?q=site:{url}", headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('a')

        indexed = any(url in str(result) for result in results)
        if indexed == True:
            return 0
        else:
            return 1

    except requests.RequestException as e:
        print(f"Error: {e}")
        return False

# UT
def index_UT():
    url = "https://example.com"
    print(check_google_index_api(url))
    print(check_google_index_chrome(url))
    print(check_google_index_requests(url))