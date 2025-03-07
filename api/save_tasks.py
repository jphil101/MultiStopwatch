import os
import json
import datetime
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def handler(request):
    """Vercel serverless function to handle task saving."""
    
    if request.method != "POST":
        return {"statusCode": 405, "body": "Method not allowed"}

    try:
        tasks = request.get_json()
    except Exception:
        return {"statusCode": 400, "body": "Invalid JSON"}
    
    today = datetime.date.today().strftime("%d/%m/%Y")

    for task in tasks:
        task_name = task.get("task_name")
        elapsed_time = task.get("elapsed_time")
        created_at = datetime.datetime.utcnow().isoformat()

        result = supabase.table("tasks").upsert(
            {
                "date": today,
                "task_name": task_name,
                "elapsed_time": elapsed_time,
                "created_at": created_at
            },
            on_conflict="date,task_name"  # Fix: Use correct string syntax
        ).execute()

        if result.get("error"):  # Fix: Check for error safely
            return {
                "statusCode": 500,
                "body": f"Error saving tasks: {result['error']}"
            }

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Tasks saved successfully"}),
        "headers": {"Content-Type": "application/json"}
    }
