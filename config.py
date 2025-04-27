import tomllib

def get_token():
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        return data['bot']['token']

def get_adminid():
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        return data['bot']['adminid']
