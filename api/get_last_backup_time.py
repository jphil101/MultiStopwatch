# api/get_last_backup_time.py
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

log(f"get_last_backup_time: SUPABASE_URL defined: {bool(SUPABASE_URL)}")
log(f"get_last_backup_time: SUPABASE_KEY defined: {bool(SUPABASE_KEY)}")

if not SUPABASE_URL or not SUPABASE_KEY:
    log("ERROR: get_last_backup_time: Missing Supabase environment variables!")
    raise ValueError("Missing Supabase environment variables!")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    log("get_last_backup_time: Supabase client created successfully")
except Exception as e:
    log(f"ERROR creating Supabase client in get_last_backup_time: {str(e)}")
    raise

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        log("==== get_last_backup_time GET request received ====")
        last_backup_time = None
        try:
            # Fetch the specific key, return null if not found
            response = supabase.table("metadata").select("value") \
                .eq("key", "last_backup_time") \
                .maybe_single() \
                .execute()

            log(f"Metadata fetch response: {response.data}") # Log fetched data

            if response.data and response.data.get("value"):
                last_backup_time = response.data["value"] # Expecting ISO string
                log(f"Found last_backup_time: {last_backup_time}")
            else:
                 log("No last_backup_time found in metadata.")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*") # CORS
            self.end_headers()
            # Return the timestamp string directly, or null
            self.wfile.write(json.dumps({"last_backup_time": last_backup_time}).encode('utf-8'))
            log("get_last_backup_time successful response sent.")

        except Exception as e:
            log(f"ERROR fetching last backup time: {str(e)}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Failed to fetch backup time: {str(e)}", "last_backup_time": None}).encode('utf-8'))

    # Optional: Handle CORS preflight requests
    def do_OPTIONS(self):
        log("==== get_last_backup_time OPTIONS request received ====")
        self.send_response(204) # No Content
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        log("OPTIONS response sent.")