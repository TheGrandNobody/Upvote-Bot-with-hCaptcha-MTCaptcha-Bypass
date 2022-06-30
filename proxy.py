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
    # Fetch all the proxies
    proxy_list = req.get(
        'https://proxy.webshare.io/api/proxy/list', headers=headers).json()['results']
    proxies = ['%s:%s' % (p['proxy_address'], p['ports']['socks5'])
               for p in proxy_list]

    return proxies
