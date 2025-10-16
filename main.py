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

# --- Supabase Connection via Transaction Pooler ---
DB_HOST = os.getenv("DB_HOST", "aws-1-us-east-2.pooler.supabase.com")
DB_PORT = os.getenv("DB_PORT", "6543")  # ✅ transaction pooler port
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres.nzqzhpeccenmgglkcmhi")  # 👈 from connection string
DB_PASS = os.getenv("DB_PASS", "Sharks@2709")

@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            sslmode="require"
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return {"message": "Login successful!"}
        else:
            return {"message": "Invalid email or password."}

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "FastAPI backend is running on Render!"}