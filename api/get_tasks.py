import os
import json
import datetime
from supabase import create_client, Client

# Initialize the Supabase client using env variables.
SUPABASE_URL = os.environ.get("SUPABASE_URL")  # Get value from environment
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
def handler(request):
    today = datetime.date.today().strftime("%d/%m/%Y")
    # Query the tasks table where date matches today
    response = supabase.table("tasks").select("*").eq("date", today).execute()
    tasks = response.data  # List of rows (each row is a dict)
    return {
        "statusCode": 200,
        "body": json.dumps(tasks),
        "headers": {"Content-Type": "application/json"}
    }
