# Annotell Authentication

Python 3 library providing foundations for Annotell Authentication
on top of the `requests` library. 

Builds on the standard Oauth 2.0 Client Credentials flow.

Set tokens in AuthSession constructor or set environment variables `ANNOTELL_CLIENT_ID` and
 `ANNOTELL_CLIENT_SECRET`
 
```python
from annotell.auth.authsession import AuthSession

auth_session = AuthSession(client_id="X", client_id="Y")

# create a requests session with automatic oauth refresh  
sess = auth_session.session

# make call to some Annotell service with your token. Use default requests 
sess.get("https://api.annotell.com")
```