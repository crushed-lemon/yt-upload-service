from azure.cosmos import CosmosDict
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from providers.idprovider import getIdentifier
import accessors.cosmosaccessor as cosmosaccessor
import accessors.blobstoreaccessor as blobstoreaccessor
import re

app = FastAPI()

# Allow frontend origin
origins = [
    "http://localhost:5137",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewVideo(BaseModel):
    video_name : str

class FileDetails(BaseModel):
    file_size : int
    chunk_size: int
    chunks: int

class Metadata(BaseModel):
    description : str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/upload/getPendingUploads/{username}")
async def get_pending_uploads(username: str):
    return [{"upload_id" : "xyz", "video_name" : "video_xyz", "percentage_uploaded" : 12, "timestamp" : 1234}, {"upload_id" : "abc", "video_name" : "video_abc", "percentage_uploaded" : 12, "timestamp" : 53647}]

@app.post("/upload/newVideo")
async def new_video(nv : NewVideo):
    upload_id = getIdentifier()
    cosmosaccessor.create("uploads", {
        "id" : upload_id,
        "upload_id" : upload_id,
        "doc_type" : "upload_info",
        "title" : nv.video_name,
        "upload_status" : "NOT_STARTED",
        "uploader" : "user1" # Replace with the user who made this request
    })
    return {"url" : upload_id}

@app.post("/upload/fileDetails/{upload_id}")
async def upload_filedetails(upload_id : str, fd : FileDetails):
    upload_details : CosmosDict = cosmosaccessor.read("uploads", upload_id)
    etag = upload_details.get("_etag")
    upload_details.update({
        "file_size" : fd.file_size,
        "chunk_size" : fd.chunk_size,
        "chunks" : fd.chunks,
        "upload_status" : "STARTED",
    })
    cosmosaccessor.put("uploads", etag, upload_details)
    return {"status" : "OK"}

@app.post("/upload/chunk/{upload_id}")
async def upload_chunks(upload_id : str, request : Request):
    chunk = await request.body()
    video_info = cosmosaccessor.read("uploads", upload_id)
    range_header = request.headers.get("Content-range")
    index = getIndex(video_info, range_header)
    blobstoreaccessor.upload_raw_blob(upload_id, chunk, index)
    cosmosaccessor.create("uploads", {
        "id" : upload_id+"_part_"+str(index),
        "upload_id" : upload_id,
        "doc_type" : "chunk_info",
        "chunk_id" : index,
    })
    return {"status" : "OK"}

@app.post("/upload/metadata/{upload_id}")
async def upload_metadata(upload_id : str, metadata : Metadata):
    video_info = cosmosaccessor.read("uploads", upload_id)
    etag = video_info.get("_etag")
    num_chunks = video_info.get("chunks")

    blobstoreaccessor.finish_upload(upload_id, num_chunks)

    video_info.update({
        "description" : metadata.description,
        "upload_status" : "COMPLETED"
    })

    cosmosaccessor.put("uploads", etag, video_info)
    return {"status" : "OK"}


def getIndex(video_info, range_header):
    match = re.match(r"bytes (\d+)-(\d+)/(\d+)", range_header)
    if not match:
        raise ValueError(f"Invalid range header: {range_header}")
    start = int(match.group(1))

    chunk_size = video_info.get("chunk_size")

    return start // chunk_size
