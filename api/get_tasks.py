# api/get_tasks.py
import os
import json
import datetime
import sys
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client

# --- Logging Setup ---
def log(message):
    print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] {message}", file=sys.stderr)
    sys.stderr.flush()
# --- End Logging Setup ---

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Use ANON key if RLS allows public read

log(f"get_tasks: SUPABASE_URL defined: {bool(SUPABASE_URL)}")
log(f"get_tasks: SUPABASE_KEY defined: {bool(SUPABASE_KEY)}")

if not SUPABASE_URL or not SUPABASE_KEY:
    log("ERROR: get_tasks: Missing Supabase environment variables!")
    raise ValueError("Missing Supabase environment variables!")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    log("get_tasks: Supabase client created successfully")
except Exception as e:
    log(f"ERROR creating Supabase client in get_tasks: {str(e)}")
    raise

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        log("==== get_tasks GET request received ====")
        try:
            # Match the date format used in save_tasks.py
            today_formatted = datetime.date.today().strftime("%d/%m/%Y")
            log(f"Fetching tasks for date: {today_formatted}")

            # Select relevant columns, order by creation time if available
            # Assuming your table has 'created_at', otherwise order by 'task_name' or primary key
            query = supabase.table("tasks").select("task_name, elapsed_time").eq("date", today_formatted) #.order("created_at", desc=False) # Add order if needed

            response = query.execute()
            log(f"Supabase tasks fetch response: {response.data}") # Log fetched data

            tasks = response.data if response.data else []
            log(f"Found {len(tasks)} tasks for today.")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*") # CORS
            self.end_headers()
            self.wfile.write(json.dumps(tasks).encode('utf-8'))
            log("get_tasks successful response sent.")

        except Exception as e:
            log(f"ERROR fetching tasks: {str(e)}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            # Send empty list on error? Or an error object? Let's send error.
            self.wfile.write(json.dumps({"error": f"Failed to fetch tasks: {str(e)}"}).encode('utf-8'))

    # Optional: Handle CORS preflight requests
    def do_OPTIONS(self):
        log("==== get_tasks OPTIONS request received ====")
        self.send_response(204) # No Content
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        log("OPTIONS response sent.")