from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import time, requests, json
from urllib.parse import quote
from supabase import create_client, Client
from fastapi.responses import JSONResponse
import openpyxl
import pandas as pd
from io import BytesIO
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

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
    bulk_files: list[UploadFile] = File(None),
):
    try:
        
        print("\n===== DEBUG: Incoming form data =====")
        print("Name:", name)
        print("Email:", email)
        print("Position:", position)
        print("File provided:", bool(file))
        print("Compressed file provided:", bool(compressed_file))
        print("Bulk files type:", type(bulk_files))
        print("Bulk files length:", len(bulk_files) if bulk_files else 0)
        if bulk_files:
            for bf in bulk_files:
                print(" - Bulk file name:", bf.filename)
        print("=====================================\n")


        debug = {}
        file_url, compressed_file_url = None, None
        bulk_file_urls = []

        debug["received_fields"] = {
            "name": name,
            "email": email,
            "position": position,
            "file_provided": bool(file),
            "compressed_provided": bool(compressed_file),
            "bulk_files_count": len(bulk_files) if bulk_files else 0,
        }

        # ---------------- NORMAL FILE UPLOAD ----------------
        if file:
            file_bytes = await file.read()
            ts = int(time.time())
            safe_filename = f"{ts}_{quote(file.filename)}"
            upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_filename}"

            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": file.content_type or "application/octet-stream",
            }

            res = requests.post(upload_url, headers=headers, data=file_bytes, timeout=30)
            debug["normal_upload_status"] = res.status_code

            if res.status_code in (200, 201):
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{safe_filename}"
            else:
                debug["normal_upload_failed"] = res.text

        # ---------------- COMPRESSED FILE UPLOAD ----------------
        if compressed_file:
            comp_bytes = await compressed_file.read()
            ts2 = int(time.time())
            safe_comp_filename = f"{ts2}_compressed_{quote(compressed_file.filename)}"
            upload_url_comp = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_comp_filename}"

            headers_comp = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": compressed_file.content_type or "application/octet-stream",
            }

            res_comp = requests.post(upload_url_comp, headers=headers_comp, data=comp_bytes, timeout=30)
            debug["compressed_upload_status"] = res_comp.status_code

            if res_comp.status_code in (200, 201):
                compressed_file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{safe_comp_filename}"
            else:
                debug["compressed_upload_failed"] = res_comp.text

        # ---------------- BULK FILE UPLOADS ----------------
        if bulk_files:
            for f in bulk_files:
                file_bytes = await f.read()
                ts3 = int(time.time())
                safe_bulk_name = f"{ts3}_bulk_{quote(f.filename)}"
                upload_url_bulk = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_bulk_name}"

                headers_bulk = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": f.content_type or "application/octet-stream",
                }

                res_bulk = requests.post(upload_url_bulk, headers=headers_bulk, data=file_bytes, timeout=30)
                debug.setdefault("bulk_upload_response_texts", []).append(res_bulk.text)

                debug.setdefault("bulk_upload_status", []).append(res_bulk.status_code)

                debug.setdefault("bulk_files_received", []).append(f.filename)


                if res_bulk.status_code in (200, 201):
                    bulk_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{safe_bulk_name}"
                    bulk_file_urls.append(bulk_url)
                else:
                    debug.setdefault("bulk_upload_failed_files", []).append(f.filename)
                    
        

        # ---------------- INSERT INTO EMPLOYEES TABLE ----------------
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
            "compressed_file_url": compressed_file_url,
            "bulk_file_urls": json.dumps(bulk_file_urls),
        }

        insert_res = requests.post(insert_url, headers=insert_headers, json=payload, timeout=30)
        debug["db_insert_status"] = insert_res.status_code

        if insert_res.status_code in (200, 201):
            return {"message": "Employee added successfully!", "debug": debug, "row": insert_res.json()}
        else:
            return {"error": "Database insert failed", "debug": debug, "db_text": insert_res.text}

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


@app.post("/bulk_upload")
async def bulk_upload(file: UploadFile = File(...)):
    try:
        # 1️⃣ Validate file type (.xlsx only)
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return JSONResponse(status_code=422, content={"error": "Only .xlsx files are supported."})

        # 2️⃣ Read Excel file
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        # 3️⃣ Clean and normalize column names safely
        df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]


        # 4️⃣ Check if required columns exist
        required_columns = ["First_Name", "Last_Name", "Gender", "Country", "Age", "Date", "Id"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required columns: {', '.join(missing)}"},
            )

        # 5️⃣ Convert date fields to string (for Supabase compatibility)
        if "Date" in df.columns:
            df["Date"] = df["Date"].astype(str)

        # 6️⃣ Prepare data for insertion
        records = df.to_dict(orient="records")

        # 7️⃣ Insert each record directly into Supabase table
        inserted_rows = 0
        for record in records:
            response = supabase.table("employee_bulk_imports").insert(record).execute()
            if response.data:
                inserted_rows += 1

        # 8️⃣ Return success message
        return JSONResponse(
            content={
                "message": f"✅ Successfully inserted {inserted_rows} rows into employee_bulk_imports",
                "status": "success",
            }
        )

    except Exception as e:
        logging.error(f"Bulk upload failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    try:
        # Validate file type
        if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            logging.error(f"Invalid file type: {file.content_type}")
            return JSONResponse(status_code=422, content={"error": "Invalid file type, only .xlsx files are allowed"})

        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        data_json = df.to_dict(orient="records")

        # Debug logs
        logging.info(f"Parsed {len(data_json)} records from Excel file")

        # Insert into Supabase
        response = supabase.table("employees_bulk_imports").insert(data_json).execute()

        if response.data:
            logging.info("Data inserted successfully into Supabase")
            return JSONResponse(content={"message": "Data uploaded successfully!", "inserted_rows": len(response.data)})
        else:
            logging.error(f"Insert failed: {response}")
            return JSONResponse(status_code=500, content={"error": "Failed to insert data into Supabase"})

    except Exception as e:
        logging.error(f"Error during bulk upload: {str(e)}")
        return JSONResponse(status_code=400, content={"error": f"An error occurred: {str(e)}"})