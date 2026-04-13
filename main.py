from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx

app = FastAPI(title="Garena Bind Web Panel", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GARENA_BASE = "https://account.garena.com"
TIMEOUT = 15.0

# ── Request Models ─────────────────────────────────────────────────────────────

class TokenRequest(BaseModel):
    access_token: str

class SendOTPRequest(BaseModel):
    access_token: str
    email: str

class VerifyOTPRequest(BaseModel):
    access_token: str
    otp: str

class VerifyIdentitySecRequest(BaseModel):
    access_token: str
    secondary_password: str

class ChangeBindRequest(BaseModel):
    access_token: str
    email: str
    otp: str
    secondary_password: Optional[str] = None

class UnbindRequest(BaseModel):
    access_token: str
    identity_token: str

# ── Helpers ────────────────────────────────────────────────────────────────────

def auth_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "GarenaBindPanel/1.0",
    }

async def garena_get(path: str, token: str, params: dict = None):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        return await client.get(
            f"{GARENA_BASE}{path}",
            headers=auth_headers(token),
            params=params or {},
        )

async def garena_post(path: str, token: str, payload: dict = None):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        return await client.post(
            f"{GARENA_BASE}{path}",
            headers=auth_headers(token),
            json=payload or {},
        )

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/bind-info")
async def bind_info(access_token: str):
    try:
        r = await garena_get("/api/bind/info", access_token)
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-otp")
async def send_otp(body: SendOTPRequest):
    try:
        r = await garena_post("/api/bind/send-otp", body.access_token, {"email": body.email})
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "message": "OTP sent successfully", "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-otp")
async def verify_otp(body: VerifyOTPRequest):
    try:
        r = await garena_post("/api/bind/verify-otp", body.access_token, {"otp": body.otp})
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "message": "OTP verified", "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-identity-sec")
async def verify_identity_sec(body: VerifyIdentitySecRequest):
    try:
        r = await garena_post("/api/bind/verify-identity-sec", body.access_token,
                              {"secondary_password": body.secondary_password})
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "message": "Identity verified", "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-identity-otp")
async def verify_identity_otp(body: VerifyOTPRequest):
    try:
        r = await garena_post("/api/bind/verify-identity-otp", body.access_token, {"otp": body.otp})
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "message": "Identity verified via OTP", "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change-bind")
async def change_bind(body: ChangeBindRequest):
    try:
        payload = {"email": body.email, "otp": body.otp}
        if body.secondary_password:
            payload["secondary_password"] = body.secondary_password
        r = await garena_post("/api/bind/change", body.access_token, payload)
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "message": "Email bound successfully", "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unbind")
async def unbind(body: UnbindRequest):
    try:
        r = await garena_post("/api/bind/unbind", body.access_token,
                              {"identity_token": body.identity_token})
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "message": "Email unbound successfully", "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel")
async def cancel_bind(body: TokenRequest):
    try:
        r = await garena_post("/api/bind/cancel", body.access_token)
        data = r.json()
        if r.status_code == 200:
            return {"success": True, "message": "Bind request cancelled", "data": data}
        return JSONResponse(status_code=r.status_code, content={"success": False, "error": data})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Garena request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
