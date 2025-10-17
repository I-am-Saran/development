from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import time
from urllib.parse import quote
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
SUPABASE_BUCKET = "employee-files"  # Replace with your actual bucket name in Supabase

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
    compressed_file: UploadFile = File(None),
):
    try:
        debug = {}
        file_url = None
        compressed_file_url = None

        debug["received_name"] = name
        debug["received_email"] = email
        debug["received_position"] = position
        debug["file_provided"] = bool(file)
        debug["compressed_file_provided"] = bool(compressed_file)

        # ---------------- NORMAL FILE UPLOAD ----------------
        if file:
            debug["file_filename"] = file.filename
            debug["file_content_type"] = file.content_type
            file_bytes = await file.read()
            debug["file_size_bytes"] = len(file_bytes)

            ts = int(time.time())
            safe_filename = f"{ts}_{quote(file.filename)}"
            upload_path = safe_filename

            upload_url_A = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{upload_path}"
            headers_A = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": file.content_type or "application/octet-stream",
            }

            try:
                resA = requests.post(upload_url_A, headers=headers_A, data=file_bytes, timeout=30)
                debug["normal_upload_A_status"] = resA.status_code
                if resA.status_code in (200, 201):
                    file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{upload_path}"
                    debug["normal_upload_method"] = "A"
                else:
                    debug["normal_upload_A_failed"] = True
            except Exception as e:
                debug["normal_upload_A_exception"] = str(e)

            if not file_url:
                upload_url_B = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}"
                headers_B = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                }
                files = {"file": (safe_filename, file_bytes, file.content_type or "application/octet-stream")}
                try:
                    resB = requests.post(upload_url_B, headers=headers_B, files=files, timeout=30)
                    debug["normal_upload_B_status"] = resB.status_code
                    if resB.status_code in (200, 201):
                        file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{upload_path}"
                        debug["normal_upload_method"] = "B"
                    else:
                        debug["normal_upload_B_failed"] = True
                except Exception as e:
                    debug["normal_upload_B_exception"] = str(e)

        # ---------------- COMPRESSED FILE UPLOAD ----------------
        if compressed_file:
            debug["compressed_filename"] = compressed_file.filename
            debug["compressed_content_type"] = compressed_file.content_type
            comp_bytes = await compressed_file.read()
            debug["compressed_file_size_bytes"] = len(comp_bytes)

            ts2 = int(time.time())
            safe_comp_filename = f"{ts2}_compressed_{quote(compressed_file.filename)}"
            upload_path_comp = safe_comp_filename

            upload_url_comp_A = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{upload_path_comp}"
            headers_comp_A = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": compressed_file.content_type or "application/octet-stream",
            }

            try:
                resCompA = requests.post(upload_url_comp_A, headers=headers_comp_A, data=comp_bytes, timeout=30)
                debug["compressed_upload_A_status"] = resCompA.status_code
                if resCompA.status_code in (200, 201):
                    compressed_file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{upload_path_comp}"
                    debug["compressed_upload_method"] = "A"
                else:
                    debug["compressed_upload_A_failed"] = True
            except Exception as e:
                debug["compressed_upload_A_exception"] = str(e)

            if not compressed_file_url:
                upload_url_comp_B = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}"
                headers_comp_B = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                }
                files_comp = {
                    "file": (safe_comp_filename, comp_bytes, compressed_file.content_type or "application/octet-stream")
                }
                try:
                    resCompB = requests.post(upload_url_comp_B, headers=headers_comp_B, files=files_comp, timeout=30)
                    debug["compressed_upload_B_status"] = resCompB.status_code
                    if resCompB.status_code in (200, 201):
                        compressed_file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{upload_path_comp}"
                        debug["compressed_upload_method"] = "B"
                    else:
                        debug["compressed_upload_B_failed"] = True
                except Exception as e:
                    debug["compressed_upload_B_exception"] = str(e)

        # ---------------- INSERT EMPLOYEE ROW ----------------
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
            "file_url": file_url,
            "compressed_file_url": compressed_file_url,  # ✅ new field
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
    

@app.get("/employees")
async def get_employees():
    try:
        url = f"{SUPABASE_URL}/rest/v1/employees?select=*"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        res = requests.get(url, headers=headers, timeout=30)

        # Debug logs
        print("GET /employees status:", res.status_code)
        print("GET /employees text:", res.text)

        if res.status_code == 200:
            employees = res.json()
            return {"employees": employees}
        else:
            return {"error": "Failed to fetch employees", "status": res.status_code, "response": res.text}

    except Exception as e:
        print("GET /employees exception:", str(e))
        return {"error": str(e)}
