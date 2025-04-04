# api/get_date.py
import datetime
import json
import sys
from http.server import BaseHTTPRequestHandler

# --- Logging Setup ---
def log(message):
    print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] {message}", file=sys.stderr)
    sys.stderr.flush()
# --- End Logging Setup ---

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        log("==== get_date GET request received ====")
        try:
            # Using ISO format YYYY-MM-DD is generally safer for consistency
            # today_iso = datetime.date.today().isoformat()
            # Or keep the original DD/MM/YYYY if your frontend/DB relies on it
            today_formatted = datetime.date.today().strftime("%d/%m/%Y")
            log(f"Generated date: {today_formatted}")

            response_data = {
                "date": today_formatted
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*") # CORS for frontend
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            log("get_date successful response sent.")

        except Exception as e:
            log(f"ERROR in get_date: {str(e)}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Failed to get date: {str(e)}"}).encode('utf-8'))

    # Optional: Handle CORS preflight requests if needed, though GET usually doesn't require it
    def do_OPTIONS(self):
        log("==== get_date OPTIONS request received ====")
        self.send_response(204) # No Content
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        log("OPTIONS response sent.")