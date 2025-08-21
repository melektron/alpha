# Kayeet game server

This is a python program that hosts the KaYeet game server listening for connections both via raw TCP Sockets and WebSockets.
It also provides a GUI for displaying players, questions, results and controlling the game (intended for use on the presenters computer).

## Clients

Clients need to open ```kayeet.me``` in their browser.

## Server

The server is to be run on the presenters computer.

Recommended: Run server using .venv on (GUI possible):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# This requires python3-tk (make sure that is installed eg apt install python3-tk on debian-based systems)
python main.py
```

Run using docker (no GUI possible by default, this runs a simpler version of the server that only asks questions in the client UI and waits for console input on the server to advance to the next question):

```bash
docker build -t kayeet-game-server .
bash start_docker.bash
```

KaYeet requires that that clients connect via SSL WebSockets (https/wss) to the KaYeet server, because of the browser security policy. To achieve this, you must use an HTTP proxy (like traefik) with a public IP address and domain that can accept encrypted HTTPS connections (possibly with Let'sEncrypt cert resolver) and proxy the requests to the presenter PC without encryption on port 1647 (should be in internal network only). This proxy is not hosted by us, you need to set it up yourself for now.

When using docker compose, the proxy is expected to be connected to the "traefik_proxy_net" docker network, and requests can be routed directly to the container, example traefik labels are provided in the default [docker-compose.yml](docker-compose.yml) file. When running the GUI version, or the proxy is on an other physical server than the computer, you must manually configure the proxy to route to the IP that your server is running on.