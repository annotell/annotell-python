---
id: annotell-auth
title: Annotell Auth
description: How to authenticate with Annotell APIs
---
Authentication is handled by [annotell-auth](https://pypi.org/project/annotell-auth/), a Python 3 library providing foundations for Annotell Authentication on top of the requests library.

Builds on the standard Oauth 2.0 Client Credentials flow. There are a few ways to provide auth credentials to our api clients. Annotell Python clients such as in  annotell-query or annotell-input-api accept an auth parameter that can be set explicitly or you can omit it and use environment variables.

To create an authenticated input-api client, simply do this:

```python
from annotell.input_api.input_api_client import InputApiClient

api_client = InputApiClient()
```
This uses the credentials found in `ANNOTELL_CREDENTIALS` environment variable. Or override explicitly:

```python
from annotell.input_api.input_api_client import InputApiClient

api_client = InputApiClient(auth="~/.config/annotell/credentials.json")
```

There are a few ways to set your credentials in auth.

- Set the environment variable `ANNOTELL_CREDENTIALS` to point to your Annotell Credentials file. The credentials will contain the Client Id and Client Secret.
- Set to the credentials file path like `auth="~/.config/annotell/credentials.json"`
- Set environment variables `ANNOTELL_CLIENT_ID` and `ANNOTELL_CLIENT_SECRET`
- Set to credentials tuple `auth=(client_id, client_secret)`

API clients such as the InputApiClient accept this auth parameter.
Under the hood, they all use the AuthSession class which is implements a requests session with automatic token refresh.




