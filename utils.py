from urllib.parse import urlparse

def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain = domain.split(':')[0]
    return domain