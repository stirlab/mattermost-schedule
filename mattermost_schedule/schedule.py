#!/usr/bin/env python3

import argparse
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import JSONResponse

from .constants import FASTAPI_HOST, FASTAPI_PORT
from .logger import Logger


class ScheduleAPI:
    """Main API class for Mattermost scheduling integration.

    Handles FastAPI setup, routing, and command processing.

    :param host: API host address
    :param port: API port number
    :param debug: Enable debug mode
    """

    def __init__(
        self, host: str = FASTAPI_HOST, port: int = FASTAPI_PORT, debug: bool = False
    ) -> None:
        self.host = host
        self.port = port
        self.debug = debug
        self.app = FastAPI()
        self.logger = Logger("ScheduleAPI", debug=debug)
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Register FastAPI routes."""
        self.app.add_api_route("/monitor", self.get_handler, methods=["GET"])
        self.app.add_api_route("/schedule", self.post_handler, methods=["POST"])

    async def _log_request_metadata(self, request: Request) -> None:
        """Log detailed request information using the logger."""
        self.logger.debug(f"Incoming {request.method} request to {request.url.path}")
        self.logger.debug(f"Headers: {dict(request.headers.items())}")

        if request.method == "GET":
            await self._log_get_request(request)
        elif request.method == "POST":
            await self._log_post_request(request)

    async def _log_get_request(self, request: Request) -> None:
        """Log details of GET requests."""
        if request.query_params:
            self.logger.debug("Query Parameters:")
            for key, value in request.query_params.items():
                self.logger.debug(f"  {key}: {value}")

    async def _log_post_request(self, request: Request) -> None:
        """Log details of POST requests."""
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            form_data = await request.form()
            for field_name, field_value in form_data.items():
                if isinstance(field_value, UploadFile):
                    self.logger.debug(f"Form field: {field_name} (file upload)")
                    self.logger.debug(f"Filename: {field_value.filename}")
                else:
                    self.logger.debug(f"Form field: {field_name}={field_value}")
        elif "application/json" in content_type:
            json_data = await request.json()
            self.logger.debug(f"JSON data: {json_data}")

    async def get_handler(self, request: Request) -> str:
        """Handle GET requests to /monitor endpoint."""
        await self._log_request_metadata(request)
        return "up"

    async def post_handler(self, request: Request) -> JSONResponse:
        """Handle POST requests to /schedule endpoint."""
        await self._log_request_metadata(request)
        try:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                return await self._handle_json_command(await request.json())
            return await self._handle_form_command(dict(await request.form()))
        except Exception as e:
            self.logger.error(f"Request processing failed: {str(e)}")
            return JSONResponse(
                content={"text": "Internal server error"}, status_code=500
            )

    async def _handle_json_command(self, data: dict[str, Any]) -> JSONResponse:
        """Process JSON command with validation."""
        is_valid, error = await self._validate_json_command(data)
        if not is_valid:
            return JSONResponse(content={"text": f"Error: {error}"}, status_code=400)
        return await self._handle_delete_command(data)

    async def _handle_form_command(self, data: dict[str, Any]) -> JSONResponse:
        """Process form command with validation."""
        is_valid, error = await self._validate_form_command(data)
        if not is_valid:
            return JSONResponse(content={"text": f"Error: {error}"}, status_code=400)
        return (
            await self._handle_list_command()
            if data.get("text") == "list"
            else JSONResponse(
                content={"text": "Error: Unknown operation. Available: list"},
                status_code=400,
            )
        )

    async def _handle_list_command(self) -> JSONResponse:
        """Handle list command with logging."""
        self.logger.info("Listing scheduled events")
        return JSONResponse(
            content={
                "text": "### Scheduled Events",
                "attachments": [
                    self.create_message_attachment(
                        "", "### 2024-02-20 10:00 AM\nTeam Meeting", 1
                    ),
                    self.create_message_attachment(
                        "", "### 2024-02-21 2:30 PM\nProject Review", 2
                    ),
                    self.create_message_attachment(
                        "", "### 2024-02-22 11:00 AM\nClient Call", 3
                    ),
                ],
            }
        )

    async def _handle_delete_command(self, data: dict[str, Any]) -> JSONResponse:
        """Handle delete command with validation."""
        message_id = data["context"]["id"]
        self.logger.info(f"Deleting scheduled message ID: {message_id}")
        return JSONResponse(
            content={"ephemeral_text": f"Scheduled message {message_id} deleted."}
        )

    @staticmethod
    def create_message_attachment(
        pretext: str, text: str, message_id: int
    ) -> dict[str, Any]:
        """Create Mattermost message attachment with delete action."""
        return {
            "pretext": pretext,
            "text": text,
            "actions": [
                {
                    "id": "delete",
                    "name": "Delete",
                    "style": "danger",
                    "integration": {
                        "url": "http://localhost:8001/schedule",
                        "context": {"action": "delete", "id": message_id},
                    },
                }
            ],
        }

    async def _validate_json_command(self, data: dict[str, Any]) -> tuple[bool, str]:
        """Validate JSON command structure."""
        if "context" not in data:
            return False, "No context provided"
        context = data["context"]
        if not isinstance(context, dict):
            return False, "Context must be a dictionary"
        if "action" not in context:
            return False, "No action specified in context"
        if context["action"] != "delete":
            return (
                False,
                f"Invalid action: {context['action']}. Only 'delete' is supported.",
            )
        if "id" not in context:
            return False, "No id specified in context"
        try:
            event_id = int(context["id"])
            if event_id <= 0:
                return False, f"Invalid id: {event_id}. Must be a positive integer."
        except (ValueError, TypeError):
            return False, f"Invalid id: {context['id']}. Must be a valid integer."
        return True, ""

    async def _validate_form_command(self, data: dict[str, Any]) -> tuple[bool, str]:
        """Validate form command structure."""
        if "command" not in data:
            return False, "No command provided"
        command = data["command"]
        if command != "/schedule":
            return False, f"Invalid command: {command}. Only /schedule is supported."
        return True, ""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Mattermost scheduling API server")
    parser.add_argument(
        "--host",
        type=str,
        default=FASTAPI_HOST,
        help="Host address to bind, default %(default)s",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=FASTAPI_PORT,
        help="Port number to listen on, default %(default)s",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main() -> None:
    """Main entry point for the schedule API server."""
    args = parse_args()
    logger = Logger("Main", debug=args.debug)
    try:
        logger.info(f"Starting server on {args.host}:{args.port}")
        api = ScheduleAPI(host=args.host, port=args.port, debug=args.debug)
        uvicorn.run(api.app, host=api.host, port=api.port)
    except Exception as e:
        logger.critical(f"Server failed: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
