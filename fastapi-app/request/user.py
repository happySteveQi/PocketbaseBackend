import httpx
import os
from fastapi import APIRouter, HTTPException
router = APIRouter()

# POCKETBASE_URL = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")
POCKETBASE_URL = os.getenv("POCKETBASE_URL", "http://pocketbase:8090")

PB_USERS_COLLECTION = "users"

from models.user import *


# 健康检查接口
@router.get("/api/health")
async def check_pocketbase_health():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{POCKETBASE_URL}/api/health")
            print("📥 PocketBase 健康检查状态:", resp.status_code)
            print("📥 PocketBase 健康检查内容:", resp.text)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print("❌ PocketBase 健康检查失败:", e.response.text)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.ConnectError as e:
            print("❌ 无法连接到 PocketBase:", str(e))
            raise HTTPException(status_code=503, detail=f"无法连接到 PocketBase: {str(e)}")

#auth
#注册接口
#创建一条user
# /api/collections/users/records
#POST
#参数
# body
# email
# password
# passwordConfirm
# 响应
# {
#   "collectionId": "_pb_users_auth_",
#   "collectionName": "users",
#   "id": "test",
#   "email": "test@example.com",
#   "emailVisibility": true,
#   "verified": true,
#   "name": "test",
#   "avatar": "filename.jpg",
#   "created": "2022-01-01 10:00:00.123Z",
#   "updated": "2022-01-01 10:00:00.123Z"
# }

@router.post("/api/user/register", response_model=UserRegisterResponse)
async def create_user(user: UserRegisterRequest):
    print("📨 注册请求参数:", user.dict())
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{POCKETBASE_URL}/api/collections/{PB_USERS_COLLECTION}/records",
                json=user.dict()
            )
            print("📥 注册响应状态:", resp.status_code)
            print("📥 注册响应内容:", resp.text)
            resp.raise_for_status()
            result = resp.json()
            # 注册成功后自动发送验证邮件
            # try:
            #     verify_resp = await client.post(
            #         f"{POCKETBASE_URL}/api/collections/{PB_USERS_COLLECTION}/request-verification",
            #         json={"email": user.email}
            #     )
            #     print("📤 自动发送验证邮件响应:", verify_resp.status_code, verify_resp.text)
            # except Exception as e:
            #     print("❌ 自动发送验证邮件失败:", e)
            return result
        except httpx.HTTPStatusError as e:
            print("❌ 注册失败:", e.response.text)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

#发送验证邮箱接口
# /api/collections/users/request-verification
# POST
#body
#入参
#email
#响应
#204 null
@router.post("/api/user/request-verification")
async def request_verification(body: RequestVerificationBody):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{POCKETBASE_URL}/api/collections/{PB_USERS_COLLECTION}/request-verification",
            json={"email": body.email}
        )
        resp.raise_for_status()
        return {"status": "verification email sent"}


#登录接口
# /api/collections/users/auth-with-password
# POST
#body
#identity: email of the record to authenticate.
#password 
#响应
# {
#   "token": "JWT_TOKEN",
#   "record": {
#     "collectionId": "_pb_users_auth_",
#     "collectionName": "users",
#     "id": "test",
#     "email": "test@example.com",
#     "emailVisibility": true,
#     "verified": true,
#     "name": "test",
#     "avatar": "filename.jpg",
#     "created": "2022-01-01 10:00:00.123Z",
#     "updated": "2022-01-01 10:00:00.123Z"
#   }
# }    
@router.post("/api/user/login", response_model=UserLoginResponse)
async def user_login(user: UserLoginRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{POCKETBASE_URL}/api/collections/{PB_USERS_COLLECTION}/auth-with-password",
            json=user.dict()
        )
        resp.raise_for_status()
        login_result = resp.json()
        # 检查邮箱是否已验证
        if not login_result.get("record", {}).get("verified", False):
            raise HTTPException(status_code=403, detail="邮箱未验证，请先验证邮箱后再登录。")
        return login_result


#更新用户信息
#/api/collections/users/records/:id
# PATCH
# Path parameters
# id
# Body Parameters
# email
# oldPassword
# password
# passwordConfirm
# name
# avatar file object
#响应
# {
#   "collectionId": "_pb_users_auth_",
#   "collectionName": "users",
#   "id": "test",
#   "email": "test@example.com",
#   "emailVisibility": true,
#   "verified": true,
#   "name": "test",
#   "avatar": "filename.jpg",
#   "created": "2022-01-01 10:00:00.123Z",
#   "updated": "2022-01-01 10:00:00.123Z"
# }
from typing import Annotated
from fastapi import Header, UploadFile, File

# 新接口：直接透传 Authorization header
@router.patch("/api/user/update", response_model=UserRegisterResponse)
async def user_update(
    user: UserUpdateRequest,
    token: Annotated[str, Header(alias="Authorization")]
):
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{POCKETBASE_URL}/api/collections/{PB_USERS_COLLECTION}/records/me",
            json=user.dict(exclude_none=True),
            headers={"Authorization": token}
        )
        resp.raise_for_status()
        return resp.json()


# 新接口：直接透传 Authorization header
@router.post("/api/user/avatar", response_model=UserRegisterResponse)
async def upload_avatar(
    token: Annotated[str, Header(alias="Authorization")],
    avatar: UploadFile = File(...)
):
    async with httpx.AsyncClient() as client:
        form = httpx.MultipartWriter()
        form.add_part(
            await avatar.read(),
            name="avatar",
            filename=avatar.filename,
            content_type=avatar.content_type
        )
        resp = await client.patch(
            f"{POCKETBASE_URL}/api/collections/{PB_USERS_COLLECTION}/records/me",
            headers={
                "Authorization": token,
                "Content-Type": form.content_type
            },
            content=await form.aread()
        )
        resp.raise_for_status()
        return resp.json()
