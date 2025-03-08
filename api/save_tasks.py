import os
import json
import datetime
import sys
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client

# Set up logging to stdout for Vercel
def log(message):
    print(message, file=sys.stderr)
    sys.stderr.flush()

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
log(f"SUPABASE_URL defined: {bool(SUPABASE_URL)}")
log(f"SUPABASE_KEY defined: {bool(SUPABASE_KEY)}")

if not SUPABASE_URL or not SUPABASE_KEY:
    log("ERROR: Missing Supabase environment variables!")
    raise ValueError("Missing Supabase environment variables!")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    log("Supabase client created successfully")
except Exception as e:
    log(f"ERROR creating Supabase client: {str(e)}")
    raise

class handler(BaseHTTPRequestHandler):  
    def do_POST(self):
        log("==== POST request received ====")
        content_length = int(self.headers.get('Content-Length', 0))
        log(f"Content length: {content_length}")
        
        post_data = self.rfile.read(content_length)
        log(f"Raw post data: {post_data}")
        
        try:
            tasks = json.loads(post_data)
            log(f"Parsed tasks: {json.dumps(tasks)}")
        except Exception as e:
            log(f"ERROR parsing JSON: {str(e)}")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {str(e)}"}).encode())
            return
        
        today = datetime.date.today().strftime("%d/%m/%Y")
        log(f"Today's date: {today}")
        
        try:
            # Process all tasks at once for better efficiency
            rows = []
            for i, task in enumerate(tasks):
                task_name = task.get("task_name")
                elapsed_time = task.get("elapsed_time")
                
                log(f"Processing task {i+1}: name='{task_name}', time='{elapsed_time}'")
                
                if not task_name:
                    log(f"Skipping task {i+1} due to empty name")
                    continue
                    
                rows.append({
                    "date": today,
                    "task_name": task_name,
                    "elapsed_time": elapsed_time,
                    "created_at": datetime.datetime.utcnow().isoformat()
                })
            
            log(f"Prepared {len(rows)} rows for insertion")
            
            if rows:
                log("Attempting to delete existing tasks for today first...")
                # Delete existing tasks for today before inserting new ones
                delete_result = supabase.table("tasks").delete().eq("date", today).execute()
                log(f"Delete result: {delete_result}")
                
                log("Now inserting new tasks...")
                # Simple insert without upsert
                result = supabase.table("tasks").insert(rows).execute()
                
                log(f"Insert result: {result}")
                
                # Proper error checking
                if hasattr(result, 'error') and result.error:
                    log(f"ERROR in insert: {result.error}")
                    raise Exception(f"Supabase error: {result.error}")
                
                log("Insert successful")
            else:
                log("No valid rows to insert")
            
            log("Sending success response")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Tasks saved successfully",
                "count": len(rows)
            }).encode())
            
        except Exception as e:
            log(f"ERROR in save_tasks: {str(e)}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": f"Failed to save tasks: {str(e)}"
            }).encode())