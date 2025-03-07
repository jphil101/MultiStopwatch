import datetime
import json

def handler(request):
    today = datetime.date.today().strftime("%d/%m/%Y")
    return {
        "statusCode": 200,
        "body": json.dumps({"date": today}),
        "headers": {"Content-Type": "application/json"}
    }
