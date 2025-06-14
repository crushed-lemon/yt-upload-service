from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
cosmos_url = "https://yt-cosmos-db.documents.azure.com:443/"
cosmos_db = "yt_cosmos_db"
cosmos_client = CosmosClient(cosmos_url, credential)
db_client = cosmos_client.get_database_client(cosmos_db)

def read(container_name : str, key : str) :
    print(container_name)
    print(key)
    return db_client.get_container_client(container_name).read_item(item=key, partition_key=key)

def create(container_name : str, value : dict) :
    db_client.get_container_client(container_name).create_item(body=value)

def put(container_name : str, etag : str, value : dict) :
    (db_client.get_container_client(container_name)
        .replace_item(
            item=value,
            body=value,
            request_options={
                "accessCondition": {
                    "type": "IfMatch",
                    "condition": etag
                }
            }
        )
    )

