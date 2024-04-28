# Kayeet game server

This is a python programm that hosts the kayeet game server listening for connections both via raw TCP Sockets or WebSockets.
It also provides a GUI for displaying players and controlling the game (intended for use on the presenters computer).

Run using venv (GUI possible):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# This requires python3-tk (make sure that is installed eg apt install python3-tk on debian-based systems)
python main.py
```

Run using docker (no GUI possible by default):

```bash
docker build -t kayeet-game-server .
bash start_docker.bash
```

This is setup to work with an external traefik proxy for SSL websockets (wss://) that is connected to the "traefik_proxy_net" docker network.