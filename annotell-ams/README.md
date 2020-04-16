# Annotell Management System

Python 3 library providing access to AMS. 

To install with pip run `pip install annotell-ams`

Set env ANNOTELL_CREDENTIALS, see [annotell-auth](https://github.com/annotell/annotell-python/tree/master/annotell-auth). 

## Metadata Example
Stream all items matching a query
```python
from annotell.ams.query import QueryClient
query_client = QueryClient()
resp = query_client.stream_metadata(query_filter="id = X")
for item in resp.items():
    print(item)
```

## Change log
- Change constructor for authentication to only accept `auth`. 