from utils import get_domain
import requests
import time
import concurrent.futures
import redis

class SubdomainCounter:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def get_subdomain_count(self, url):
        domain = get_domain(url)
        cached_count = self.redis.get(f"subdomain_count:{domain}")
        if cached_count is not None:
            print("Cached: Subdomain")
            return int(cached_count)
        
        #at_IFqjecj2qOKRWgzWvHqxJg9PDbVAN
        api_endpoint = "https://subdomains.whoisxmlapi.com/api/v1?apiKey=at_IFqjecj2qOKRWgzWvHqxJg9PDbVAN&domainName="   
        #api_endpoint = "https://subdomains.whoisxmlapi.com/api/v1?apiKey=at_P0N8Toc4J4uLTe6bEiDInbMFIBpaF&domainName="


        try:
            response = requests.get(api_endpoint + domain)
            if response.status_code == 200:
                data = response.json()
                subdomains = []
                if 'result' in data and 'records' in data['result']:
                    subdomains = [record['domain'] for record in data['result']['records']]

                if len(subdomains) == 0:
                    self.redis.set(f"subdomain_count:{domain}", 1, ex=2592000)  
                    return 1
                
                # add domain/subdomain itself.
                self.redis.set(f"subdomain_count:{domain}", len(subdomains), ex=2592000)

                # add others.
                self.add_domain_to_database(subdomains)
                print("get_subdomain_count: not exist in the cache.")
                return len(subdomains)
            else:
                print("Error: Unable to access subdomain API")
                self.redis.set(f"subdomain_count:{domain}", 1, ex=2592000)
                return 1
        except Exception as e:
            print(f"get_subdomain_count Error: {e}")
            self.redis.set(f"subdomain_count:{domain}", 1, ex=2592000)
            return 1


    # As it is a demo, we just use a cache instead of database.
    def add_domain_to_database(self, subdomains):
        n = len(subdomains)
        for k in subdomains:
            self.redis.set(f"subdomain_count:{k}", n, ex=2592000)