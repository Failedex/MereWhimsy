#! /usr/bin/env python3

import sys 
import asyncio 
from i3ipc.aio import Connection

SOCK = "/tmp/.i3-float.sock"

class FloatManage: 
    def __init__(self): 
        self.i3 = None
        self.floating = False

    async def connect(self): 
        self.i3 = await Connection().connect()
        self.i3.on("window::new", self.new_win)

    async def new_win(self, i3, event):
        if self.floating: 
            await event.container.command('floating enable')
            await event.container.command('move position center')
    
    async def update_win(self, state): 
        root = await self.i3.get_tree()

        for output in root.nodes: 
            if output.name == "__i3": 
                continue 

            for l in output.descendants(): 
                if not l.app_id:
                    continue
                if l.app_id in ["sterm", "sncmpcpp", "sranger"]:
                    continue
                await l.command('floating ' + state)

    async def run(self): 
        async def handle(reader, writer): 
            data = await reader.read(1024)
            
            if data == b'float': 
                self.floating = True
            elif data == b'tile':
                self.floating = False
            elif data == b'toggle': 
                self.floating = not self.floating

            await self.update_win("enable" if self.floating else "disable")
            print("false" if self.floating else "true", flush=True)

        server = await asyncio.start_unix_server(handle, SOCK)
        await server.serve_forever()

async def run_server(): 
    manager = FloatManage()
    await manager.connect()
    await manager.run()

async def send_msg(msg): 
    reader, writer = await asyncio.open_unix_connection(SOCK)

    writer.write(msg.encode())
    await writer.drain() 

    writer.close()
    await writer.wait_closed()

if __name__ == "__main__": 
    a = sys.argv[1]

    if a in ["float", "tile", "toggle"]:
        asyncio.run(send_msg(a))

    if a == "subscribe": 
        asyncio.run(run_server())

