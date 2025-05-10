import requests
from requests.auth import HTTPBasicAuth
from authors.models import Node  # You’ll need a Node model

def fetch_remote_author(node, author_id):
    url = f"{node.host}/api/authors/{author_id}/"
    response = requests.get(url, auth=HTTPBasicAuth(node.username, node.password))
    if response.status_code == 200:
        return response.json()
    return None

def fetch_remote_posts(node, author_id):
    url = f"{node.host}/api/authors/{author_id}/posts/"
    response = requests.get(url, auth=HTTPBasicAuth(node.username, node.password))
    if response.status_code == 200:
        return response.json()
    return []
