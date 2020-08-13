import json
import os
from dataclasses import dataclass
from typing import Optional

REQUIRED_CREDENTIALS_FILE_KEYS = ["clientId", "clientSecret", "email", "userId", "issuer"]

@dataclass
class AnnotellCredentials:
    client_id: str
    client_secret: str
    email: str
    user_id: int
    issuer: str


def parse_credentials(path: str):
    try:
        with open(path) as f:
            credentials = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find Annotell Credentials file at {path}")

    if not isinstance(credentials, dict):
        raise AttributeError(f"Could not json dict from {path}")

    for k in REQUIRED_CREDENTIALS_FILE_KEYS:
        if k not in credentials:
            raise KeyError(f"Missing key {k} in credentials file")

    return AnnotellCredentials(
        client_id=credentials.get("clientId"),
        client_secret=credentials.get("clientSecret"),
        email=credentials.get("email"),
        user_id=credentials.get("userId"),
        issuer=credentials.get("issuer")
    )


def get_credentials(auth):
    if isinstance(auth, str):
        if auth.endswith(".json"):
            return parse_credentials(auth)
        raise ValueError("Bad auth credentials file, must be json")
    elif isinstance(auth, AnnotellCredentials):
        return auth
    else:
        raise ValueError("Bad auth credentials, must be path to credentials file, or AnnotellCredentials object")


def get_credentials_from_env():
    creds = os.getenv("ANNOTELL_CREDENTIALS")
    if creds:
        client_credentials = parse_credentials(creds)
        return client_credentials.client_id, client_credentials.client_secret

    client_id = os.getenv("ANNOTELL_CLIENT_ID")
    client_secret = os.getenv("ANNOTELL_CLIENT_SECRET")

    return client_id, client_secret

def resolve_credentials(auth=None,
                        client_id: Optional[str] = None,
                        client_secret: Optional[str] = None):
    has_credentials_tuple = client_id is not None and client_secret is not None
    if auth is not None:
        if has_credentials_tuple:
            raise ValueError("Choose either auth or client_id+client_secret")
        if isinstance(auth, tuple):
            if len(auth) != 2:
                raise ValueError("Credentials tuple must be tuple of (client_id, client_secret)")
            client_id, client_secret = auth
        else:
            creds = get_credentials(auth)
            client_id = creds.client_id
            client_secret = creds.client_secret
    elif not has_credentials_tuple:
        client_id, client_secret = get_credentials_from_env()

    return client_id, client_secret

if __name__ == '__main__':
    credentials = get_credentials_from_env()
    print(credentials)
