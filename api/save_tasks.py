import os
import json
import datetime
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            tasks = json.loads(post_data)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return
        
        today = datetime.date.today().strftime("%d/%m/%Y")

        for task in tasks:
            task_name = task.get("task_name")
            elapsed_time = task.get("elapsed_time")
            created_at = datetime.datetime.utcnow().isoformat()  # Current timestamp

            # Use UPSERT to update if task_name & date already exist
            result = supabase.table("tasks").upsert({
                "date": today,
                "task_name": task_name,
                "elapsed_time": elapsed_time,
                "created_at": created_at  # Update created_at on each save
            }, on_conflict=["date", "task_name"]).execute()

            if result.error:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error saving tasks: {result.error}".encode())
                return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Tasks saved successfully"}).encode())