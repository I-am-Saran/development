from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import time
import psycopg2
from urllib.parse import quote
import os
import requests
app = FastAPI()

# Allow frontend communication (update with your frontend URL later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Supabase REST API credentials ---
SUPABASE_URL = "https://nzqzhpeccenmgglkcmhi.supabase.co"  # replace with your Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im56cXpocGVjY2VubWdnbGtjbWhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ2NzAzMSwiZXhwIjoyMDc2MDQzMDMxfQ.z5qf6unizb_KaF8YKpc60V2jsP54v-NsKclDW9zfYEU"  # replace with your Supabase Service Role Key

@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        # REST API query to Supabase users table
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}&password=eq.{password}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
        )

        users = res.json()

        if users:
            return {"message": "Login successful!"}
        else:
            return {"message": "Invalid email or password."}

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "FastAPI backend is running on Render!"}

@app.post("/add-employee")
async def add_employee(
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(...),
    file: UploadFile = File(None),
):
    try:
        debug = {}
        file_url = None

        # 0) Basic request debug
        debug["received_name"] = name
        debug["received_email"] = email
        debug["received_position"] = position
        debug["file_provided"] = bool(file)

        # 1) If no file provided, just insert with file_url = None
        if not file:
            debug["note"] = "No file provided; inserting row with file_url = null"
        else:
            # Report file metadata
            debug["file_filename"] = file.filename
            debug["file_content_type"] = file.content_type

            # Read file bytes (once)
            file_bytes = await file.read()
            debug["file_size_bytes"] = len(file_bytes)

            # prepare safe unique filename
            ts = int(time.time())
            safe_filename = f"{ts}_{quote(file.filename)}"
            upload_path = safe_filename

            # Method A: try binary POST to /storage/v1/object/{bucket}/{path}
            upload_url_A = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{upload_path}"
            headers_A = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": file.content_type or "application/octet-stream",
            }
            try:
                resA = requests.post(upload_url_A, headers=headers_A, data=file_bytes, timeout=30)
                debug["upload_A_status"] = resA.status_code
                debug["upload_A_text"] = resA.text[:1000]
                if resA.status_code in (200, 201):
                    file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{upload_path}"
                    debug["upload_method"] = "A"
                else:
                    debug["upload_A_failed"] = True
            except Exception as e:
                debug["upload_A_exception"] = str(e)

            # If Method A failed, try Method B: multipart form upload to /storage/v1/object/{bucket}
            if not file_url:
                upload_url_B = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}"
                headers_B = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    # do not set Content-Type here; requests will set boundary for multipart
                }
                files = {
                    "file": (safe_filename, file_bytes, file.content_type or "application/octet-stream")
                }
                try:
                    resB = requests.post(upload_url_B, headers=headers_B, files=files, timeout=30)
                    debug["upload_B_status"] = resB.status_code
                    debug["upload_B_text"] = resB.text[:1000]
                    if resB.status_code in (200, 201):
                        # supabase public URL for this object
                        file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{upload_path}"
                        debug["upload_method"] = "B"
                    else:
                        debug["upload_B_failed"] = True
                except Exception as e:
                    debug["upload_B_exception"] = str(e)

            if not file_url:
                debug["file_upload_overall_failed"] = True

        # 2) Insert employee row (include file_url which may be None)
        insert_url = f"{SUPABASE_URL}/rest/v1/employees"
        insert_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        payload = {
            "name": name,
            "email": email,
            "position": position,
            "file_url": file_url
        }

        insert_res = requests.post(insert_url, headers=insert_headers, json=payload, timeout=30)
        debug["insert_status"] = insert_res.status_code
        debug["insert_text"] = insert_res.text[:1000]

        if insert_res.status_code in (200, 201):
            return {"message": "Employee added successfully!", "debug": debug, "row": insert_res.json()}
        else:
            return {"error": "DB insert failed", "debug": debug, "db_text": insert_res.text}

    except Exception as e:
        return {"error": str(e)}
    
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        SUPABASE_BUCKET = "employee-files"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{file.filename}"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": file.content_type,
        }

        res = requests.post(upload_url, headers=headers, data=await file.read())

        if res.status_code in [200, 201]:
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file.filename}"
            return {"file_url": file_url}
        else:
            return {"error": res.text}

    except Exception as e:
        return {"error": str(e)}