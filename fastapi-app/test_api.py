import httpx
import asyncio

BASE_URL = "http://127.0.0.1:6000"
# BASE_URL = "http://8.140.195.241/api"

async def test_register_login():
    print("📨 测试注册用户")
    import time
    # email = f"testuser_{int(time.time())}@example.com"
    email = f"444835397@qq.com"
    user_data = {
        "email": email,
        "password": "12345678",
        "passwordConfirm": "12345678",
        "name": "TestUser"
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/api/user/register", json=user_data)
        print("注册响应状态码:", r.status_code)

        try:
            print("注册响应 JSON:", r.json())
        except Exception:
            print("❌ 注册响应不是 JSON，原始内容:")
            print(r.text)

        # print("📤 请求发送验证邮件")
        # r = await client.post(f"{BASE_URL}/api/user/request-verification", json={"email": user_data["email"]})
        # print("验证邮件响应:", r.status_code, r.json() if r.content else "No content")

        print("🔐 登录用户")
        r = await client.post(f"{BASE_URL}/api/user/login", json={
            "identity": user_data["email"],
            "password": user_data["password"]
        })
        login_result = r.json()
        print("登录响应:", r.status_code, login_result)

        token = login_result.get("token")
        user_id = login_result.get("record", {}).get("id")

        return token, user_id

async def test_note_crud(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        print("📝 创建 note")
        r = await client.post(
            f"{BASE_URL}/api/notes",
            json={"title": "Test Note", "content": "This is a note."},
            headers=headers
        )
        print("创建 note 响应状态码:", r.status_code)
        print("响应原始内容:", r.text)
        try:
            note = r.json()
        except Exception:
            print("❌ note 创建响应不是 JSON")
            print("响应原始内容:", r.text)
            return

        note_id = note.get("id")
        if not note_id:
            print("❌ 无法获取 note_id，终止测试")
            return

        print("📄 获取 note")
        r = await client.get(
            f"{BASE_URL}/api/notes/{note_id}",
            headers=headers
        )
        print("获取响应:", r.status_code, r.json())

        print("✏️ 更新 note")
        r = await client.patch(
            f"{BASE_URL}/api/notes/{note_id}",
            json={"title": "Updated Title", "content": "Updated content"},
            headers=headers
        )
        print("更新响应:", r.status_code, r.json())

        # print("🗑️ 删除 note")
        # r = await client.delete(
        #     f"{BASE_URL}/api/notes/{note_id}",
        #     headers=headers
        # )
        # print("删除响应:", r.status_code)

async def main():
    token, user_id = await test_register_login()
    # await test_note_crud(token)

if __name__ == "__main__":
    asyncio.run(main())
