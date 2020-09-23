# Annotell Cloud Storage

Python 3 library providing access to Annotell Cloud Storage

To install with pip run `pip install annotell-cloud-storage`

This is mostly a thin wrapper on top of Google's own GCP (Google Cloud Platform) Storage library

See https://cloud.google.com/storage/docs/uploading-objects

## GCP Example
Set env GOOGLE_APPLICATION_CREDENTIALS to your credentials file path
```python
from annotell.cloud_storage import gcp
bucket_name = "my-bucket"
gcp.list_blobs(bucket_name)
```

# Change log

0.5.0 remove check to enforce that GOOGLE_APPLICATION_CREDENTIALS are set