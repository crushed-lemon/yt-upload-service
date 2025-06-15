
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import base64

AZURE_BLOB_URL = "https://ytstorage2.blob.core.windows.net"
AZURE_CONTAINER_NAME_RAW = 'yt-video-raw'
AZURE_CONTAINER_NAME_PROCESSED = 'yt-video-processed'
AZURE_BLOB_NAME = '<video_id>.mp4'

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(AZURE_BLOB_URL, credential)
raw_container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME_RAW)
processed_container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME_PROCESSED)

def upload_raw_blob(upload_id : str, data : bytes, index : int) :
    block_id = base64.b64encode(f"{index:06}".encode()).decode()
    blob_client = raw_container_client.get_blob_client(upload_id)
    blob_client.stage_block(block_id, data)

def finish_upload(upload_id : str, num_chunks : int) :
    block_ids = []
    for i in range(num_chunks):
        block_id = base64.b64encode(f"{i:06}".encode()).decode()
        block_ids.append(block_id)

    blob_client = raw_container_client.get_blob_client(upload_id)
    blob_client.commit_block_list(block_ids)
