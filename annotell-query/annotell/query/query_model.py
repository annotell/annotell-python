from .util import iter_streaming_items

class AbstractQueryResponse(object):
    def items(self):
        raise NotImplementedError

class QueryResponse(AbstractQueryResponse):
    def __init__(self, response):
        self.raw_response = response
        self.status_code = response.status_code
        self._json = None

    @property
    def json(self):
        if self._json is None:
            self._json = self.raw_response.json()
        return self._json

    def items(self):
        return self.json['items']

    @property
    def total_hits(self):
        return self.json['totalHits']

    @property
    def took(self):
        return self.json['took']

    @property
    def returned_hits(self):
        return self.json['returnedHits']

    @property
    def aggregates(self):
        return self.json.get("aggregates") or dict()

    @property
    def head(self):
        return self.items()[0] if self.returned_hits > 0 else None

class StreamingQueryResponse(AbstractQueryResponse):

    def __init__(self, response):
        self.raw_response = response
        self.status_code = response.status_code

    def items(self):
        return iter_streaming_items(self.raw_response)


class QueryException(RuntimeError):
    pass
