from models.note import *
from fastapi import Query, Path, APIRouter
import httpx
import os
from typing import Annotated, Optional
from fastapi import Header, HTTPException
import base64
import json

router = APIRouter()

POCKETBASE_URL = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")
PB_NOTES_COLLECTION = "notes"




#查询note列表
#get
# /api/collections/notes/records
#参数
#query 参数
#page
#perPage
#sort
#filter
#返回值
# {
#   "page": 1,
#   "perPage": 30,
#   "totalPages": 1,
#   "totalItems": 2,
#   "items": [
#     {
#       "collectionId": "pbc_3395098727",
#       "collectionName": "notes",
#       "id": "test",
#       "title": "test",
#       "content": "test",
#       "created": "2022-01-01 10:00:00.123Z",
#       "updated": "2022-01-01 10:00:00.123Z"
#     },
#     {
#       "collectionId": "pbc_3395098727",
#       "collectionName": "notes",
#       "id": "[object Object]2",
#       "title": "test",
#       "content": "test",
#       "created": "2022-01-01 10:00:00.123Z",
#       "updated": "2022-01-01 10:00:00.123Z"
#     }
#   ]
# }
@router.get("/api/notes/items", response_model=NoteListResponse)
async def note_list(
    page: int = Query(1, ge=1),
    perPage: int = Query(30, ge=1),
    sort: str = Query("-created"),
    filter: Optional[str] = Query(""),
    token: Annotated[Optional[str], Header(alias="Authorization")] = None
):
    headers = {"Authorization": token} if token else {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{POCKETBASE_URL}/api/collections/{PB_NOTES_COLLECTION}/records",
            params={"page": page, "perPage": perPage, "sort": sort, "filter": filter},
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()

#获取一条note
#get
# /api/collections/notes/records/:id
#参数
#path id
#响应
# {
#   "collectionId": "pbc_3395098727",
#   "collectionName": "notes",
#   "id": "test",
#   "title": "test",
#   "content": "test",
#   "created": "2022-01-01 10:00:00.123Z",
#   "updated": "2022-01-01 10:00:00.123Z"
# }
@router.get("/api/notes/{note_id}", response_model=NoteRecordResponse)
async def read_note(note_id: str = Path(...), token: Annotated[Optional[str], Header(alias="Authorization")] = None):
    headers = {"Authorization": token} if token else {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{POCKETBASE_URL}/api/collections/{PB_NOTES_COLLECTION}/records/{note_id}",
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()

#创建一条note
# /api/collections/notes/records
#POST
#参数
#title
#content
# 响应
# {
#   "collectionId": "pbc_3395098727",
#   "collectionName": "notes",
#   "id": "test",
#   "title": "test",
#   "content": "test",
#   "created": "2022-01-01 10:00:00.123Z",
#   "updated": "2022-01-01 10:00:00.123Z"
# }
@router.post("/api/notes", response_model=NoteRecordResponse)
async def create_note(
    note: NoteCreateRequest,
    token: Annotated[str, Header(alias="Authorization")]
):
    try:
        # 解码 JWT payload
        payload_b64 = token.split('.')[1]
        padding = '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding)
        payload = json.loads(payload_json)
        user_id = payload["id"]
    except Exception as e:
        print("❌ 解析 token 出错：", e)
        raise HTTPException(status_code=500, detail="Token 解析失败")

    data = note.dict()
    data["user"] = user_id

    print("📤 创建笔记 payload：", data)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{POCKETBASE_URL}/api/collections/{PB_NOTES_COLLECTION}/records",
            json=data,
            headers={"Authorization": token}
        )
        print("📥 PocketBase 响应状态:", resp.status_code)
        print("📥 PocketBase 响应内容:", resp.text)
        resp.raise_for_status()
        return resp.json()

#更新一条note
#PATCH
# /api/collections/notes/records/:id
#path
#参数
#id
# 响应
# {
#   "collectionId": "pbc_3395098727",
#   "collectionName": "notes",
#   "id": "test",
#   "title": "test",
#   "content": "test",
#   "created": "2022-01-01 10:00:00.123Z",
#   "updated": "2022-01-01 10:00:00.123Z"
# }
@router.patch("/api/notes/{note_id}", response_model=NoteRecordResponse)
async def update_note(note_id: str = Path(...), note: NoteCreateRequest = ..., token: Annotated[Optional[str], Header(alias="Authorization")] = None):
    headers = {"Authorization": token} if token else {}
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{POCKETBASE_URL}/api/collections/{PB_NOTES_COLLECTION}/records/{note_id}",
            json=note.dict(),
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()

#删除一条note
#DELETE
# /api/collections/notes/records/:id
#path
#参数
#id
# 响应
#204 null
@router.delete("/api/notes/{note_id}", status_code=204)
async def delete_note(note_id: str = Path(...), token: Annotated[Optional[str], Header(alias="Authorization")] = None):
    headers = {"Authorization": token} if token else {}
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{POCKETBASE_URL}/api/collections/{PB_NOTES_COLLECTION}/records/{note_id}",
            headers=headers
        )
        resp.raise_for_status()
