from utils import get_domain
import requests
import time
import concurrent.futures

cache = {}

def subdomain_number(url):
    subdomain_number = get_subdomain_count(url)
    return subdomain_number

    
def get_subdomain_count(url):
    global cache
    print(cache)
    domain = get_domain(url)
    if domain in cache:
        print("get_subdomain_count: exists in the cache.")
        return cache[domain]
    api_endpoint = "https://api.subdomain.center/?domain="
    try:
        response = requests.get(api_endpoint + domain, timeout=10)
        if response.status_code == 200:
            subdomains = response.json()
            for k in subdomains:
                print(k)
            add_domain_to_database(subdomains)
            print("get_subdomain_count: not exist in the cache.")
            return len(subdomains)
        else:
            print("Error: Unable to access subdomain API")
            return -1
    except Exception as e:
        print(f"get_subdomain_count Error: {e}")
        return -1


# As it is a demo, we just use a cache instead of database.
def add_domain_to_database(subdomains):
    global cache
    n = len(subdomains)
    for k in subdomains:
        cache[k] = n

# UT to test search time and cache time
def domain_count_UT():
    start_time = time.time()
    print(get_subdomain_count("https://wwei.one"))
    
    search_time = time.time()
    print("search time: ", search_time - start_time)

    print(get_subdomain_count("https://bio.wwei.one"))
    cache_time = time.time()
    print("cache time: ", cache_time - search_time)

# domain_count_UT()

# UT to test timeout
def domain_count_UT_2():
    subdomain_number("https://wwei.one")
    # if timeout will continue to search and add to the database.
    time.sleep(20)
    subdomain_number("https://bio.wwei.one")

# domain_count_UT_2()