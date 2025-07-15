import requests
import random

PROXY_SOURCE_URL = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"

def fetch_proxies():
    try:
        response = requests.get(PROXY_SOURCE_URL, timeout=10)
        proxy_list = response.text.strip().split('\n')
        return [proxy.strip() for proxy in proxy_list if proxy.strip()]
    except Exception as e:
        print(f"[ERROR] Failed to fetch proxy list: {e}")
        return []

def get_random_proxy():
    proxies = fetch_proxies()
    if not proxies:
        raise Exception("No proxies available from ProxyScrape.")
    return random.choice(proxies)
