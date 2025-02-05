#!/usr/bin/env python3

from fastapi import FastAPI, Request, UploadFile
import uvicorn

from .constants import (
    FASTAPI_HOST,
    FASTAPI_PORT,
)

app = FastAPI()

async def print_request_metadata(request: Request):
    """Print detailed information about the request"""
    print("\n----- Incoming Request -----")
    print(f"Method: {request.method}")
    url = request.url
    print("Path Details:")
    print(f"  Full Path: {url}")
    print(f"  Scheme: {url.scheme}")
    print(f"  Network Location: {url.netloc}")
    print(f"  Path: {url.path}")
    print(f"  Query String: {url.query}")
    print("Headers:")
    for name, value in request.headers.items():
        print(f"  {name}: {value}")

async def print_get_metadata(request: Request):
    await print_request_metadata(request)
    if request.query_params:
        print("Query Parameters:")
        for key, value in request.query_params.items():
            print(f"  {key}: {value}")
    else:
        print("No query parameters.")
    print("----- End of GET Request -----\n")

async def print_post_metadata(request: Request,):
    await print_request_metadata(request)
    content_type = request.headers.get('content-type', '')
    if 'multipart/form-data' in content_type:
        form_data = await request.form()
        for field_name, field_value in form_data.items():
            if isinstance(field_value, UploadFile):
                print(f"  {field_name} (file upload):")
                print(f"    Filename: {field_value.filename}")
                print(f"    Content-Type: {field_value.content_type}")
                content = await field_value.read()
                print(f"    Size: {len(content)} bytes")
            else:
                print(f"  {field_name}: {field_value}")
    elif 'application/x-www-form-urlencoded' in content_type:
        form_data = await request.form()
        print("Parsed URL-encoded Form Data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")
    else:
        body = await request.body()
        print(f"Raw POST Data: {body}")
        print("Content type not recognized for parsing. Displaying raw data only.")
    print("----- End of POST Request -----\n")

@app.get("/monitor")
async def get_handler(request: Request):
    await print_get_metadata(request)
    return "up"

@app.post("/schedule")
async def post_handler(request: Request):
    await print_post_metadata(request)
    form_data = await request.form()
    form_dict = dict(form_data)
    response = await handle_command(form_dict)
    return response

async def validate_command(form_data: dict) -> tuple[bool, str]:
    """Validate the Mattermost slash command.
    Returns (is_valid, error_message)"""
    if 'command' not in form_data:
        return False, "No command provided"
    command = form_data['command']
    if command != '/schedule':
        return False, f"Invalid command: {command}. Only /schedule is supported."
    return True, ""

def create_message_attachment(pretext: str, text: str, messsage_id: int) -> dict:
    """Create a Mattermost message attachment for an message"""
    return {
        "pretext": pretext,
        "text": text,
        "actions": [{
            "id": "delete",
            "name": "Delete",
            "integration": {
                "url": "http://localhost:8001",
                "context": {
                    "action": "delete",
                    "id": messsage_id
                }
            }
        }]
    }

async def handle_list_command() -> dict:
    """Handle the /schedule list command"""
    events = [
        create_message_attachment("2024-02-20 10:00 AM", "Team Meeting", 1),
        create_message_attachment("2024-02-21 2:30 PM", "Project Review", 2),
        create_message_attachment("2024-02-22 11:00 AM", "Client Call", 3),
    ]

    return {
        "text": "### Scheduled Events",
        "attachments": events
    }

async def handle_delete_command() -> str:
    """Handle the /schedule delete command"""
    return "Deleted the scheduled message."

async def handle_command(form_data: dict) -> dict:
    """Process the Mattermost slash command"""
    is_valid, error = await validate_command(form_data)
    if not is_valid:
        return {"text": f"Error: {error}"}
    text = form_data.get('text', '').strip()
    if text == 'list':
        response_text = await handle_list_command()
    elif text == 'delete':
        response_text = await handle_delete_command()
    else:
        response_text = "Error: Unknown operation. Available operations: list, delete"
    return {"text": response_text}

def main():
    print(f"Starting FastAPI server on host {FASTAPI_HOST}, port {FASTAPI_PORT}. Use Ctrl+C to stop.")
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT)

if __name__ == "__main__":
    main()
