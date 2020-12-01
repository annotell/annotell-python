#!/bin/bash

echo "Using source $(pwd)/.."
echo "Using destination $(pwd)/../../docs"
docker run --rm --name slate -v $(pwd)/../../docs:/srv/slate/build -v $(pwd)/..:/srv/slate/source slatedocs/slate