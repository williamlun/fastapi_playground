import stores.mykeycloak


def login(username: str, password: str):
    return stores.mykeycloak.login(username, password)
