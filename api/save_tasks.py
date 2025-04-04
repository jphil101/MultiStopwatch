# api/save_tasks.py
import os
import json
import datetime
import sys
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client
# from supabase import PostgrestAPIResponse # Uncomment if using supabase-py v1 for detailed checks

# --- Logging Setup ---
def log(message):
    print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] {message}", file=sys.stderr)
    sys.stderr.flush()
# --- End Logging Setup ---

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Use SERVICE_ROLE key if possible for writes

log(f"save_tasks: SUPABASE_URL defined: {bool(SUPABASE_URL)}")
log(f"save_tasks: SUPABASE_KEY defined: {bool(SUPABASE_KEY)}")

if not SUPABASE_URL or not SUPABASE_KEY:
    log("ERROR: save_tasks: Missing Supabase environment variables!")
    raise ValueError("Missing Supabase environment variables!")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    log("save_tasks: Supabase client created successfully")
except Exception as e:
    log(f"ERROR creating Supabase client in save_tasks: {str(e)}")
    raise

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        log("==== save_tasks POST request received ====")
        content_length = int(self.headers.get('Content-Length', 0))
        log(f"Content length: {content_length}")
        post_data = self.rfile.read(content_length)
        log(f"Raw post data (first 500 chars): {post_data[:500]}") # Log snippet

        tasks = []
        try:
            tasks = json.loads(post_data)
            log(f"Parsed tasks (count): {len(tasks)}")
        except Exception as e:
            log(f"ERROR parsing JSON in save_tasks: {str(e)}")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {str(e)}"}).encode())
            return

        # Ensure date format matches what get_tasks expects, or use DATE type in DB
        today = datetime.date.today().strftime("%d/%m/%Y")
        log(f"Today's date for filtering/saving: {today}")

        task_operation_successful = False
        metadata_update_error = None
        rows_processed_count = 0

        try:
            # --- Task Processing Logic ---
            rows_to_insert = []
            for i, task in enumerate(tasks):
                task_name = task.get("task_name")
                elapsed_time = task.get("elapsed_time")
                # Basic validation
                if not task_name or not isinstance(task_name, str):
                     log(f"Skipping task {i+1} due to invalid/empty name: {task_name}")
                     continue
                if not elapsed_time or not isinstance(elapsed_time, str):
                     log(f"Skipping task {i+1} ('{task_name}') due to invalid/empty time: {elapsed_time}")
                     continue

                log(f"Processing task {i+1}: name='{task_name}', time='{elapsed_time}'")
                rows_to_insert.append({
                    "date": today,
                    "task_name": task_name.strip(), # Trim whitespace
                    "elapsed_time": elapsed_time,
                     # Use timezone-aware UTC time for created_at (assuming column exists)
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                })

            rows_processed_count = len(rows_to_insert)
            log(f"Prepared {rows_processed_count} valid rows for task insertion")

            if rows_to_insert:
                log("Attempting to delete existing tasks for today first...")
                # Use try-except for DB operations
                try:
                    delete_result = supabase.table("tasks").delete().eq("date", today).execute()
                    log(f"Task delete result: {delete_result.data}") # Log data part
                    # Add specific error checks for delete_result if needed (supabase-py v1/v2 differ)
                    # e.g., if hasattr(delete_result, 'error') and delete_result.error: raise ...
                except Exception as del_e:
                     log(f"ERROR deleting tasks: {str(del_e)}")
                     raise # Re-raise to be caught by outer try-except

                log("Now inserting new tasks...")
                try:
                    insert_result = supabase.table("tasks").insert(rows_to_insert).execute()
                    log(f"Task insert result: {insert_result.data}") # Log data part
                    # Add specific error checks for insert_result if needed
                    # e.g., if hasattr(insert_result, 'error') and insert_result.error: raise ...
                    task_operation_successful = True # Mark as success if no exception
                    log("Task insert operation completed.")
                except Exception as ins_e:
                    log(f"ERROR inserting tasks: {str(ins_e)}")
                    raise # Re-raise
            else:
                # If no valid tasks were submitted, maybe still delete old ones? Or just skip.
                # Current logic: Delete old ones only if new ones are provided.
                log("No valid task rows to insert, potentially leaving existing tasks for today untouched.")
                # Consider if an empty valid list should clear the day's tasks
                # If saving an empty list means "clear today", uncomment deletion here:
                # try:
                #     log("Attempting to delete existing tasks for today as input list was empty/invalid...")
                #     delete_result = supabase.table("tasks").delete().eq("date", today).execute()
                #     log(f"Task delete result (empty list): {delete_result.data}")
                # except Exception as del_empty_e:
                #      log(f"ERROR deleting tasks (empty list): {str(del_empty_e)}")
                #      raise # Re-raise
                task_operation_successful = True # Still considered successful for metadata update if no valid tasks were sent

            # --- Metadata Update Logic ---
            # Update metadata regardless of whether tasks were actually inserted,
            # as long as the request itself was processed without major error up to this point.
            # If you only want to update on *actual* task changes, move this inside the 'if rows_to_insert:' block
            log("Attempting to update last backup time metadata.")
            try:
                # Store time as UTC ISO 8601 string
                last_backup_iso_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

                meta_update_result = supabase.table("metadata").upsert({
                    "key": "last_backup_time", # The primary key
                    "value": last_backup_iso_time
                    # 'updated_at' will be set by the database default
                }).execute()

                log(f"Metadata upsert result: {meta_update_result.data}") # Log data part
                # Add specific error checks if needed
                # e.g., if hasattr(meta_update_result, 'error') and meta_update_result.error: raise ...
                log("Last backup time updated successfully.")

            except Exception as meta_e:
                metadata_update_error = str(meta_e)
                log(f"ERROR updating last backup time in metadata: {metadata_update_error}")
                # Decide if this error should prevent a 200 OK response - maybe not, log it as warning.


            # --- Send Response ---
            log("Sending success response")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response_body = {
                "message": "Tasks processed successfully",
                "count": rows_processed_count # Number of valid tasks processed
            }
            if metadata_update_error:
                response_body["metadata_warning"] = f"Failed to update metadata: {metadata_update_error}"
            self.wfile.write(json.dumps(response_body).encode())

        except Exception as e:
            # General error during task processing or metadata update
            log(f"ERROR in save_tasks processing: {str(e)}")
            # Consider more specific error codes if possible
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Failed to process tasks: {str(e)}"}).encode())

    def do_OPTIONS(self):
        log("==== save_tasks OPTIONS request received ====")
        self.send_response(204) # No Content
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        log("OPTIONS response sent.")