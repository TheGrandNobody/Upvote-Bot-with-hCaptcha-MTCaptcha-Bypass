from typing import List
import requests as req


def get_proxies(proxy_key: str) -> List[str]:
    """ Fetches a proxy list from https://proxy.webshare.io/ 
    and ensures that the IP of this computer is authorized to use them.

    Args:
        proxy_key (str): The API key for the Webshares Proxy service

    Returns:
        List[str]: A list of high anonimity, high bandwidth SOCKS5 proxies
    """
    # Obtain current IP address
    current_ip = req.get('https://api.ipify.org/?format=json').json()['ip']
    # Obtain current authorized IP address
    headers = {'Authorization': 'Token %s' % proxy_key}
    config = req.get(
        'https://proxy.webshare.io/api/proxy/config/', headers=headers)
    if config.json()['authorized_ips'][0] != current_ip:
        req.post("https://proxy.webshare.io/api/proxy/config/",
                 json={"authorized_ips": [current_ip]}, headers=headers)
    # Fetch all the proxies
    proxy_list = req.get(
        'https://proxy.webshare.io/api/proxy/list', headers=headers).json()['results']
    proxies = ['%s:%s' % (p['proxy_address'], p['ports']['socks5'])
               for p in proxy_list]

    return proxies
