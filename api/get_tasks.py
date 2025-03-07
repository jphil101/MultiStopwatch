import os
import json
import datetime
from supabase import create_client, Client

# Initialize the Supabase client using env variables.
SUPABASE_URL = os.environ.get("https://untbyduhxszwtvhoydds.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVudGJ5ZHVoeHN6d3R2aG95ZGRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwMjg3MTMsImV4cCI6MjA1NDYwNDcxM30.e6Ok23sZFaxrC2XokeJerFlnDi541_BZ0ybwF_lWZ58")
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
