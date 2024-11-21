from channels.generic.websocket import AsyncJsonWebsocketConsumer

class VideoCallConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.user = None
        self.room_id = None
        self.room_group_name = None

        self.data = {}
        self.user_data = None
        self.video_call_room_data = None

        await self.accept()


    async def receive_json(self, content):
        print("VideoCallConsumers: receive_json")
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        other_user_id = content.get("other_user_id", None)
        room_id = content.get("room_id", None)
        room_data = content.get("room_data", None)
        room_candidate = content.get("room_candidate", None)
        offer = content.get("offer", None)
        answer = content.get("answer", None)

        try:
            if command == "get_video_call":



