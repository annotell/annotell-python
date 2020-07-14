import json

def iter_streaming_items(resp):
    # parse each line as a json document
    for item in resp.iter_lines():
        if item.startswith(b"{"):
            item = item if not item.endswith(b",") else item[:-1]
            yield json.loads(item)
