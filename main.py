from fastapi import FastAPI, Query, Body
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
import httpx
import hashlib
import os

app = FastAPI(title="Garena Bind Web Panel")

# ---------- Config ----------
BASE_URL = "https://100067.connect.garena.com"
HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Encoding": "gzip"
}
APP_ID = "100067"

def sha256_hash(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

# ---------- Serve Frontend ----------
@app.get("/")
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Panel Loading...</h1>")

# ---------- API Endpoints ----------

@app.get("/bind-info")
async def get_bind_info(access_token: str = Query(...)):
    url = f"{BASE_URL}/game/account_security/bind:get_bind_info"
    params = {"app_id": APP_ID, "access_token": access_token}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, headers=HEADERS, params=params)
    return r.json()


@app.post("/send-otp")
async def send_otp(
    access_token: str = Body(...),
    email: str = Body(...)
):
    url = f"{BASE_URL}/game/account_security/bind:send_otp"
    data = {
        "app_id": APP_ID,
        "access_token": access_token,
        "email": email,
        "locale": "en_PK",
        "region": "PK"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=HEADERS, data=data)
    return r.json()


@app.post("/verify-otp")
async def verify_otp(
    access_token: str = Body(...),
    email: str = Body(...),
    otp: str = Body(...)
):
    url = f"{BASE_URL}/game/account_security/bind:verify_otp"
    data = {
        "app_id": APP_ID,
        "access_token": access_token,
        "email": email,
        "otp": otp
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=HEADERS, data=data)
    return r.json()


@app.post("/verify-identity-otp")
async def verify_identity_otp(
    access_token: str = Body(...),
    email: str = Body(...),
    otp: str = Body(...)
):
    url = f"{BASE_URL}/game/account_security/bind:verify_identity"
    data = {
        "app_id": APP_ID,
        "access_token": access_token,
        "email": email,
        "otp": otp
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=HEADERS, data=data)
    return r.json()


@app.post("/verify-identity-sec")
async def verify_identity_sec(
    access_token: str = Body(...),
    code: str = Body(...)
):
    url = f"{BASE_URL}/game/account_security/bind:verify_identity"
    data = {
        "app_id": APP_ID,
        "access_token": access_token,
        "secondary_password": sha256_hash(code)
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=HEADERS, data=data)
    return r.json()


@app.post("/change-bind")
async def change_bind(
    access_token: str = Body(...),
    identity_token: str = Body(...),
    verifier_token: str = Body(...),
    new_email: str = Body(...)
):
    url = f"{BASE_URL}/game/account_security/bind:create_rebind_request"
    data = {
        "app_id": APP_ID,
        "access_token": access_token,
        "identity_token": identity_token,
        "verifier_token": verifier_token,
        "email": new_email
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=HEADERS, data=data)
    return r.json()


@app.post("/unbind")
async def unbind(
    access_token: str = Body(...),
    identity_token: str = Body(...)
):
    url = f"{BASE_URL}/game/account_security/bind:unbind_identity"
    data = {
        "app_id": APP_ID,
        "access_token": access_token,
        "identity_token": identity_token
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=HEADERS, data=data)
    return r.json()


@app.post("/cancel")
async def cancel(access_token: str = Body(...)):
    url = f"{BASE_URL}/game/account_security/bind:cancel_request"
    data = {
        "app_id": APP_ID,
        "access_token": access_token
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=HEADERS, data=data)
    return r.json()


# ---------- Vercel Handler ----------
handler = Mangum(app)

# ---------- Local Run ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
