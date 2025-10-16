from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

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