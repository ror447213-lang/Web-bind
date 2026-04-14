from fastapi import FastAPI, Query, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import hashlib

app = FastAPI(title="Garena Bind Web Panel")

# ---------- Configuration ----------
BASE_URL = "https://100067.connect.garena.com"
HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Encoding": "gzip"
}
APP_ID = "100067"

def sha256_hash(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

# ---------- Frontend ----------
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# ---------- Endpoints ----------

@app.get("/bind-info")
async def get_bind_info(access_token: str = Query(...)):
    url = f"{BASE_URL}/game/account_security/bind:get_bind_info"
    params = {"app_id": APP_ID, "access_token": access_token}
    r = requests.get(url, headers=HEADERS, params=params)
    return r.json()


@app.api_route("/send-otp", methods=["GET", "POST"])
async def send_otp(access_token: str, email: str):
    url = f"{BASE_URL}/game/account_security/bind:send_otp"
    data = {
        "app_id": APP_ID,
        "access_token": access_token,
        "email": email,
        "locale": "en_PK",
        "region": "PK"
    }
    r = requests.post(url, headers=HEADERS, data=data)
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
    r = requests.post(url, headers=HEADERS, data=data)
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
    r = requests.post(url, headers=HEADERS, data=data)
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
    r = requests.post(url, headers=HEADERS, data=data)
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
    r = requests.post(url, headers=HEADERS, data=data)
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
    r = requests.post(url, headers=HEADERS, data=data)
    return r.json()


@app.post("/cancel")
async def cancel(access_token: str = Body(...)):
    url = f"{BASE_URL}/game/account_security/bind:cancel_request"
    data = {
        "app_id": APP_ID,
        "access_token": access_token
    }
    r = requests.post(url, headers=HEADERS, data=data)
    return r.json()


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
