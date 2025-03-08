import os
import json
import datetime
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client

# Load environment variables
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
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Invalid JSON: {str(e)}".encode())
            return
        
        today = datetime.date.today().strftime("%d/%m/%Y")
        
        try:
            # Process all tasks at once for better efficiency
            rows = []
            for task in tasks:
                task_name = task.get("task_name")
                elapsed_time = task.get("elapsed_time")
                
                if not task_name:  # Skip empty task names
                    continue
                    
                rows.append({
                    "date": today,
                    "task_name": task_name,
                    "elapsed_time": elapsed_time,
                    "created_at": datetime.datetime.utcnow().isoformat()
                })
            
            if rows:
                # Use the correct upsert method
                result = supabase.table("tasks").upsert(
                    rows,
                    on_conflict=["date", "task_name"]  # Specify columns as a list
                ).execute()
                
                # Proper error checking
                if hasattr(result, 'error') and result.error:
                    raise Exception(f"Supabase error: {result.error}")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Tasks saved successfully",
                "count": len(rows)
            }).encode())
            
        except Exception as e:
            print(f"Error in save_tasks: {str(e)}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": f"Failed to save tasks: {str(e)}"
            }).encode())