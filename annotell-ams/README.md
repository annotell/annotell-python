# Annotell Management System

Python 3 library providing access to AMS. 

To install with pip run `pip install annotell-ams`

Set env ANNOTELL_CREDENTIALS, see [annotell-auth](https://github.com/annotell/annotell-python/tree/master/annotell-auth). 

## Metadata Example
Stream all items matching a query
```python
from annotell.ams.query import QueryApiClient
query_client = QueryApiClient()
resp = query_client.stream_metadata(query_filter="id = X")
for item in resp.items():
    print(item)
```

## Change log
2.0.0
- Rename QueryApi to QueryApiClient
- Add KPI query method

1.3.0
- Change constructor for authentication to only accept `auth`. 