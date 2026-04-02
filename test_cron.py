import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=Kamillatoolkit2"
    async with websockets.connect(uri) as ws:
        # Ask to create health check
        await ws.send(json.dumps({"content": "Create a health check for this chat that runs every 15 minutes. Each run should check for LMS backend errors in the last 15 minutes and post a summary here."}))
        resp1 = await asyncio.wait_for(ws.recv(), timeout=120)
        print("CREATE RESPONSE:", resp1[:500])
        
        await asyncio.sleep(2)
        # List scheduled jobs
        await ws.send(json.dumps({"content": "List scheduled jobs."}))
        resp2 = await asyncio.wait_for(ws.recv(), timeout=60)
        print("LIST RESPONSE:", resp2[:500])

asyncio.run(main())
