import requests
from utils import paths, outputs


def users(auth_header):
    outputs.users(requests.get(paths.users, headers=auth_header))
