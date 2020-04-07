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


def get_credentials_from_env(api_token: Optional[str] = None):
    creds = os.getenv("ANNOTELL_CREDENTIALS")
    if creds:
        client_credentials = parse_credentials(creds)
        return client_credentials.client_id, client_credentials.client_secret

    client_id = os.getenv("ANNOTELL_CLIENT_ID")
    client_secret = os.getenv("ANNOTELL_CLIENT_SECRET")

    # support ANNOTELL_API_TOKEN as client_secret temporarily
    if client_id is None and client_secret is None:
        static_api_token = api_token or os.getenv("ANNOTELL_API_TOKEN")
        if static_api_token is not None:
            client_id = ""
            client_secret = static_api_token
    return client_id, client_secret

if __name__ == '__main__':
    credentials = get_credentials_from_env()
    print(credentials)
