# Annotell Query API Client

Python 3 library providing access to the Annotell Query API. 

To install with pip run `pip install annotell-query`

Set env ANNOTELL_CREDENTIALS, see [annotell-auth](https://github.com/annotell/annotell-python/tree/master/annotell-auth). 

## Judgement Query Example
Stream all items matching a query
```python
from annotell.query.query_api_client import QueryApiClient
query_client = QueryApiClient()
resp = query_client.query_judgements(query_filter="requestId = X")
for item in resp.items():
    print(item)
```

## Change log

2.1.0
- Use server default query limits 

2.0.0
- Rename library to annotell-query
- Rename QueryApi to QueryApiClient
- Add KPI query method

1.3.0
- Change constructor for authentication to only accept `auth`. 