import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=Kamillatoolkit2"
    async with websockets.connect(uri) as ws:
        # First trigger the failure
        await ws.send(json.dumps({"content": "What labs are available?"}))
        resp1 = await asyncio.wait_for(ws.recv(), timeout=60)
        print("RESPONSE1:", resp1[:300])
        
        # Now ask for investigation
        await asyncio.sleep(1)
        await ws.send(json.dumps({"content": "What went wrong? Check logs and traces."}))
        resp2 = await asyncio.wait_for(ws.recv(), timeout=120)
        print("RESPONSE2:", resp2[:2000])

asyncio.run(main())
