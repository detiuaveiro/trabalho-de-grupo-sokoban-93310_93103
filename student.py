import asyncio
import getpass
import json
import os
import time

import websockets
from mapa import Map

# Next 4 lines are not needed for AI agents, please remove them from your code!
from sokoban import Sokoban
from tree_search import *

async def agent_loop(server_address="localhost:8000", agent_name="student"):
	async with websockets.connect(f"ws://{server_address}/player") as websocket:

		# Receive information about static game properties
		await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
		
		domain = Sokoban()
		while True:
			try:
				update = json.loads(
					await websocket.recv()
				)  # receive game update, this must be called timely or your game will get out of sync with the server

				if "map" in update:
					# we got a new level
					game_properties = update
					mapa = Map(update["map"])
					
					p = SearchProblem(domain,mapa)
					t = SearchTree(p,'a*')

					for key in t.search():
						print("key : ",key)
						time.sleep(1)
						await websocket.send(
							json.dumps({"cmd": "key", "key": key})
						)  # send key command to server - you must implement this send in the AI agent

				else:
					# we got a current map state update
					state = update

			except websockets.exceptions.ConnectionClosedOK:
				print("Server has cleanly disconnected us")
				return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
