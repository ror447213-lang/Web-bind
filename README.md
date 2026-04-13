# Garena Bind Web Panel

A dark-theme web dashboard for managing Garena account email binding.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn main:app --reload
```

Then open http://localhost:8000 in your browser.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /bind-info?access_token=... | Fetch current bind email |
| POST | /send-otp | Send OTP to email |
| POST | /verify-otp | Verify OTP code |
| POST | /verify-identity-sec | Verify identity via secondary password |
| POST | /verify-identity-otp | Verify identity via OTP (change-email flow) |
| POST | /change-bind | Bind or change email |
| POST | /unbind | Unbind email |
| POST | /cancel | Cancel pending bind request |

Interactive API docs available at: http://localhost:8000/docs

## Features

- **Bind Info** — Query current bound email
- **Bind Email** — 3-step guided flow: Send OTP → Verify OTP → Bind
- **Change Email** — 4-step flow with old/new OTP verification
- **Unbind Email** — Remove bound email using identity token
- **Cancel Bind** — Abort any pending bind request
- **Console Log** — Live terminal-style output of all API calls
