[![CI](https://github.com/weni-ai/SentenX/actions/workflows/ci.yaml/badge.svg)](https://github.com/weni-ai/SentenX/actions/workflows/ci.yaml) [![codecov](https://codecov.io/github/weni-ai/SentenX/graph/badge.svg?token=HKHVFE9KBU)](https://codecov.io/github/weni-ai/SentenX)

# SentenX

microservice that uses a sentence transformer model to index and search records.

## Table of Contents

1. [Requirements](#requirements)
2. [Quickstart](#quickstart)
3. [Usage](#usage)
4. [Test](#test)

## Requirements

* python 3.10
* elasticsearch 8.9.1

## Quickstart
on root directory of this project run the following commands to:

setup sagemaker required keys and elasticsearch url environment variables

```
export AWS_ACCESS_KEY_ID=YOUR_SAGEMAKER_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SAGEMAKER_AWS_SECRET_ACCESS_KEY
export ELASTICSEARCH_URL=YOUR_ELASTICSEARCH_URL
```

install poetry
```
pip install poetry
```

create a python 3.10 virtual environment
```
poetry env use 3.10
```

activate the environment
```
poetry shell
```

install dependencies
```
poetry install
```

start the microservice
```
uvicorn app.main:main_app.api --reload
```

### Docker compose

to start sentenx with elasticsearch with docker compose:

setup `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` on `docker-compose.yml`
```
docker compose up -d
```

to stop:
```
docker compose down
```

to start with rebuild after any change on source:
```
docker compose up -d --build
```


## Usage

### To index a product

request:
```bash
curl -X PUT http://localhost:8000/products/index \
-H 'Content-Type: application/json' \
-d '{
    "catalog_id": "cat1",
    "product": {
        "facebook_id": "123456789",
        "title": "massa para bolo de baunilha",
        "org_id": "1",
        "channel_id": "5",
        "catalog_id": "cat1",
        "product_retailer_id": "pp1"
    }
}
'
```
response:
```json
status: 200
{
    "catalog_id": "cat1",
    "documents": [
        "cac65148-8c1d-423c-a022-2a52cdedcd3c"
    ]
}
```

### To index products in batch

request:
```bash

curl -X PUT http://localhost:8000/products/batch \
-H 'Content-Type: application/json' \
-d '{
    "catalog_id": "asdfgh",
    "products": [
        {
            "facebook_id": "1234567891",
            "title": "banana prata 1kg",
            "org_id": "1",
            "channel_id": "5",
            "catalog_id": "asdfgh",
            "product_retailer_id": "p1"
        },
        {
            "facebook_id": "1234567892",
            "title": "doce de banana 250g",
            "org_id": "1",
            "channel_id": "5",
            "catalog_id": "asdfgh",
            "product_retailer_id": "p2"
        }
    ]
}'
```

response:
```json
status: 200

{
    "catalog_id": "asdfgh",
    "documents": [
        "f5b8d394-eb62-4c92-9501-51a8ebcf1380",
        "bcb551e8-0bd1-4ca7-825b-cf8aa8a3f0e0"
    ]
}
```

### To search for products

request
```bash
curl http://localhost:8000/products/search \
-H 'Content-Type: application/json' \
-d '{
    "search": "massa",
    "filter": {
        "catalog_id": "cat1"
    },
    "threshold": 1.6
}
'
```
response:
```json
status: 200
{
    "products": [
        {
            "facebook_id": "1",
            "title": "massa para bolo de baunilha",
            "org_id": "1",
            "channel_id": "5",
            "catalog_id": "asdfgh4321",
            "product_retailer_id": "abc321"
        }
    ]
}
```

## Test

we use unittest with discover to run the tests that are in `./app/tests`
```
coverage run -m unittest discover -s app/tests
```

