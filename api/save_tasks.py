import os
import json
import datetime
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")  # Get value from environment
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def handler(request):
    # Only allow POST requests.
    if request.method != "POST":
        return {"statusCode": 405, "body": "Method not allowed"}
    
    try:
        tasks = request.get_json()
    except Exception:
        return {"statusCode": 400, "body": "Invalid JSON"}
    
    today = datetime.date.today().strftime("%d/%m/%Y")
    
    # Prepare rows to insert: each task should have a task_name and elapsed_time.
    rows = []
    for task in tasks:
        rows.append({
            "date": today,
            "task_name": task.get("task_name"),
            "elapsed_time": task.get("elapsed_time")
        })
    
    result = supabase.table("tasks").insert(rows).execute()
    
    if result.error:
        return {"statusCode": 500, "body": f"Error saving tasks: {result.error}"}
    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Tasks saved successfully"}),
        "headers": {"Content-Type": "application/json"}
    }
