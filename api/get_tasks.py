import os
import json
import datetime
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        today = datetime.date.today().strftime("%d/%m/%Y")

        response = supabase.table("tasks").select("*").eq("date", today).execute()
        tasks = response.data if response.data else []

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(tasks).encode())
