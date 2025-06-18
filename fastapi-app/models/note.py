
from pydantic import BaseModel
from typing import List, Optional

# 创建/更新 Note 请求模型
class NoteCreateRequest(BaseModel):
    title: str
    content: str

# Note 单条记录响应模型
class NoteRecordResponse(BaseModel):
    collectionId: str
    collectionName: str
    id: str
    title: str
    content: str
    created: str
    updated: str

# Note 列表分页响应模型
class NoteListResponse(BaseModel):
    page: int
    perPage: int
    totalPages: int
    totalItems: int
    items: List[NoteRecordResponse]