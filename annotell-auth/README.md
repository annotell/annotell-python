# Annotell Authentication

Python 3 library providing foundations for Annotell Authentication
on top of the `requests` library. 

Builds on the standard Oauth 2.0 Client Credentials flow. There are a few ways to provide auth credentials to our api
 clients. Annotell Python clients such as in `annotell-ams`, or `annotell-input-api` accept an `auth` parameter that
  can be set explicitly or you can omit it and use environment variables. 

There are a few ways to set your credentials in `auth`. 
1. Set the environment variable `ANNOTELL_CREDENTIALS` to point to your Annotell Credentials file. 
The credentials will contain the Client Id and Client Secret.
2. Set to the credentials file path like `auth="~/.config/annotell/credentials.json"` 
3. Set environment variables `ANNOTELL_CLIENT_ID` and`ANNOTELL_CLIENT_SECRET`
4. Set to credentials tuple `auth=(client_id, client_secret)` 

API clients such as the `InputApiClient` accept this `auth` parameter.

Under the hood, they all use the AuthSession class which is implements a `requests` session with automatic token
 refresh.    
```python
from annotell.auth.authsession import AuthSession

auth_session = AuthSession()

# create a requests session with automatic oauth refresh  
sess = auth_session.session

# make call to some Annotell service with your token. Use default requests 
sess.get("https://api.annotell.com")
```

## Changelog

### 1.5
Add FaultTolerantAuthRequestSession that handles token refresh on long running sessions. 

### 1.4
- Add support for `auth` parameter, with path to credentials file or `AnnotellCredentials` object
- Drop support for legacy API token

