from fastapi import FastAPI, Request, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from storage import Storage
from download_rules import DownloadRules

import settings


app = FastAPI()

storage = Storage(settings.STORAGE_PATH)
download_rules = DownloadRules(
    settings.MAX_FILE_COUNT,
    settings.DOWNLOAD_RATE_LIMIT_SIZE_BYTES,
    settings.DOWNLOAD_RATE_LIMIT_TIME_SECS,
)


@app.get("/health")
async def health():
    return {}


@app.get("/files")
async def get_all_files_metadata():
    return {
        "files": [
            {
                "name": file_metadata["name"],
                "url": app.url_path_for("download_file", file_id=file_metadata["id"]),
            }
            for file_metadata in storage.get_files_metadata()
        ]
    }


@app.get("/files/{file_id}")
async def download_file(file_id: str, request: Request):
    file_metadata = storage.get_file_metadata(file_id)
    if not file_metadata:
        raise HTTPException(
            status_code=404,
            detail=f"File with id '{file_id}' does not exist",
        )
    client_ip = request.client.host
    if download_rules.is_ip_over_download_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Download rate limit reached")
    download_rules.register_download(client_ip, file_metadata["size"])
    return FileResponse(path=file_metadata["path"], filename=file_metadata["name"])


@app.post("/files", status_code=status.HTTP_201_CREATED)
async def save_file(file: UploadFile):
    if download_rules.has_file_count_reached_limit(storage.get_file_count()):
        raise HTTPException(
            status_code=400,
            detail=f"Reached limit of {settings.MAX_FILE_COUNT} files",
        )
    file_contents = await file.read()
    saved_file_id = storage.save_file(file.filename, file_contents)
    return {
        "name": file.filename,
        "url": app.url_path_for("download_file", file_id=saved_file_id),
    }
