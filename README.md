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

## Usage

### To index a product

request:
```bash
curl -X POST http://localhost:8000/products/index \
-H 'Content-Type: application/json' \
-d '{
  "id": "1",
  "title": "leite em pó 200g",
  "org_id": "1",
  "channel_id": "5",
  "catalog_id": "asdfgh4321",
  "product_retailer_id": "abc321"
}'
```
response:
```json
{
    "page_content": "leite em pó 200g",
    "metadata": {
        "id": "1",
        "title": "leite em pó 200g",
        "org_id": "1",
        "channel_id": "5",
        "catalog_id": "asdfgh4321",
        "product_retailer_id": "abc321"
    }
}
```

### To index products in batch

request:
```bash

curl -X POST http://localhost:8000/products/batch \
-H 'Content-Type: application/json' \
-d '[
  {
    "id": "2",
    "title": "chocolate em pó 200g",
    "org_id": "1",
    "channel_id": "5",
    "catalog_id": "asdfgh1234",
    "product_retailer_id": "abc123"
  },
  {
    "id": "3",
    "title": "café 250g",
    "org_id": "1",
    "channel_id": "5",
    "catalog_id": "zxcvbn5678",
    "product_retailer_id": "def456"
  }
]'
```

response:
```json
[
    {
        "page_content": "chocolate em pó 200g",
        "metadata": {
            "id": "2",
            "title": "chocolate em pó 200g",
            "org_id": "1",
            "channel_id": "5",
            "catalog_id": "asdfgh1234",
            "product_retailer_id": "abc123"
        }
    },
    {
        "page_content": "café 250g",
        "metadata": {
            "id": "3",
            "title": "café 250g",
            "org_id": "1",
            "channel_id": "5",
            "catalog_id": "zxcvbn5678",
            "product_retailer_id": "def456"
        }
    }
]
```

### To search for products

request
```bash
curl http://localhost:8000/products/search \
-H 'Content-Type: application/json' \
-d '{
  "search": "leite em pó",
  "filter": {
      "channel_id": "5"
  },
  "threshold": 1.6
}'
```
response:
```json
{
    "products": [
        {
            "id": "1",
            "title": "leite em pó 200g",
            "org_id": "1",
            "channel_id": "5",
            "catalog_id": "asdfgh4321",
            "product_retailer_id": "abc321",
            "shop": null
        }
    ]
}
```

## Test

we use unittest with discover to run the tests that are in `./app/tests`
```
python -m unittest discover ./app/tests
```
