from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

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
    return {"url" : "ab54s"}

@app.post("/upload/fileDetails/{video_id}")
async def upload_filedetails(fd : FileDetails):
    return {"status" : "OK"}

@app.post("/upload/chunk/{video_id}")
async def upload_chunks(video_id : str, request : Request):
    chunk = await request.body()
    return {"status" : "OK"}

@app.post("/upload/metadata/{video_id}")
async def upload_chunks(video_id : str, metadata : Metadata):
    return {"status" : "OK"}
