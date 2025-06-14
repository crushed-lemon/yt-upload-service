from azure.cosmos import CosmosDict
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from providers.idprovider import getIdentifier
import accessors.cosmosaccessor as cosmosaccessor

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
        "title" : nv.video_name,
        "upload_status" : "NOT_STARTED",
        "uploader" : "user1" # Replace with the user who made this request
    })
    return {"url" : upload_id}

@app.post("/upload/fileDetails/{upload_id}")
async def upload_filedetails(upload_id : str, fd : FileDetails):
    upload_details : CosmosDict = cosmosaccessor.read("uploads", upload_id)
    print(upload_details)
    etag = upload_details.get("_etag")
    upload_details.update({
        "file_size" : fd.file_size,
        "chunk_size" : fd.chunk_size,
        "chunks" : fd.chunks,
        "uploaded_chunks" : 0,
        "upload_status" : "STARTED",
    })
    cosmosaccessor.put("uploads", etag, upload_details)
    return {"status" : "OK"}

@app.post("/upload/chunk/{upload_id}")
async def upload_chunks(upload_id : str, request : Request):
    chunk = await request.body()
    return {"status" : "OK"}

@app.post("/upload/metadata/{upload_id}")
async def upload_metadata(upload_id : str, metadata : Metadata):
    return {"status" : "OK"}
