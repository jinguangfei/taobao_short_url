from typing import Dict, Tuple
import urllib.parse

def parse_url(url: str) -> Tuple[str,Dict]:
    url_params = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(url_params.query)
    for k, v in query_params.items():
        query_params[k] = v[0]
    url_params = url_params._asdict() # convert to dict 
    url_path = url_params.get("scheme") + "://" + url_params.get("netloc") + url_params.get("path")
    return url_path,query_params