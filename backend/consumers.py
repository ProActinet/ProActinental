import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer

class DaemonWatcherConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract username and email from the query string
        query_string = self.scope["query_string"].decode()
        qs = parse_qs(query_string)
        self.username = qs.get("username", ["Unknown"])[0]
        self.email = qs.get("email", ["Unknown"])[0]

        # Define the group name for broadcasting messages
        self.group_name = "alerts"

        # Add this connection to the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected: {self.username} ({self.email})")

    async def disconnect(self, close_code):
        # Remove this connection from the group when disconnected
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("WebSocket disconnected.")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            print("Received invalid JSON.")
            return

        # Attach username/email if not provided in the message
        if "username" not in data:
            data["username"] = self.username
        if "email" not in data:
            data["email"] = self.email

        # Broadcast the message to all clients in the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast_message",
                "message": data,
            }
        )
        print("Broadcasted message:", data)

        # Forward the message to the frontend client
        await self.channel_layer.group_send(
            "frontend_logs",  # This group is used by FrontendLogConsumer
            {
                "type": "log_message",  # Must match the handler name in FrontendLogConsumer
                "message": data,
            }
        )
        print("Broadcasted message to alerts and forwarded to frontend_logs:", data)

    async def broadcast_message(self, event):
        message = event["message"]
        # Forward the message to the connected client
        await self.send(text_data=json.dumps(message))

class FrontendLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # You can capture any query parameters if needed
        self.group_name = "frontend_logs"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print("Frontend client connected to logs.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("Frontend client disconnected.")

    async def log_message(self, event):
        # event["message"] contains the log data from Golang
        message = event["message"]
        await self.send(text_data=json.dumps(message))