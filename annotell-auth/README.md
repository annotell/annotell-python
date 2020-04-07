# Annotell Authentication

Python 3 library providing foundations for Annotell Authentication
on top of the `requests` library. 

Builds on the standard Oauth 2.0 Client Credentials flow.

There are a few ways to set your credentials. 
1. Set the environment variable `ANNOTELL_CREDENTIALS` to point to your Annotell Credentials file. 
The credentials will contain the Client Id and Client Secret. 
2. Set environment variables `ANNOTELL_CLIENT_ID` and
 `ANNOTELL_CLIENT_SECRET`
3. Set tokens in the constructor with `AuthSession(client_id="X", client_id="Y")`
 
 
```python
from annotell.auth.authsession import AuthSession

auth_session = AuthSession()

# create a requests session with automatic oauth refresh  
sess = auth_session.session

# make call to some Annotell service with your token. Use default requests 
sess.get("https://api.annotell.com")
```