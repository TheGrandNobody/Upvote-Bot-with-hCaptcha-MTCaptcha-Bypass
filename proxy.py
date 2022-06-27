from typing import List
import requests as req
import pandas as pd


def get_proxies(ping: int) -> List[str]:
    """ Fetches proxies from websites to produce a list of high anonimity, SOCKS5 proxies with a maximum given ping

    Args:
        ping (int): A ping threshold for the maximum ping you want your proxies to have.

    Returns:
        List[str]: A list of high anonimity, SOCKS5 proxies with a maximum specified ping.
    """
    proxies = []
    res = req.get('https://hidemy.name/en/proxy-list/?maxtime={}&type=5&anon=4#list'.format(str(ping)),
                  headers={'User-Agent': 'Mozilla/5.0'})
    df = pd.read_html(res.content)[0]
    for _, row in df.iterrows():
        proxies.append('{}:{}'.format(row['IP address'], row['Port']))

    return proxies
