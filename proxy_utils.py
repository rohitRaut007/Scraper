# proxy_utils.py

import requests

def fetch_proxies():
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite"
    try:
        response = requests.get(url, timeout=10)
        proxy_list = response.text.strip().split("\n")
        print(f"[PROXY] Loaded {len(proxy_list)} proxies")
        return proxy_list
    except Exception as e:
        print(f"[ERROR] Failed to fetch proxies: {e}")
        return []

def test_proxy(proxy):
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
        if r.status_code == 200:
            return True
    except:
        pass
    return False

def get_working_proxies(limit=5):
    all_proxies = fetch_proxies()
    working = []

    for proxy in all_proxies:
        proxy = proxy.strip()
        if not proxy:
            continue
        print(f"[TESTING] {proxy}")
        if test_proxy(proxy):
            print(f"[OK] Working proxy: {proxy}")
            working.append(proxy)
            if len(working) >= limit:
                break
        else:
            print(f"[FAIL] {proxy}")
    return working
