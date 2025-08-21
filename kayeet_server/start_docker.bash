
docker run \
    -it --rm \
    --name kayeet-server \
    -v .:/usr/src/app \
    --network traefik_proxy_net \
    --label traefik.enable=true \
    --label traefik.http.services.kayeet-gameserver.loadbalancer.server.port=1647 \
    --label traefik.http.routers.kayeet-gameserver-router.entrypoints=websecure \
    --label traefik.http.routers.kayeet-gameserver-router.tls.certresolver=main-resolver \
    --label traefik.http.routers.kayeet-gameserver-router.rule=Host\(\`game.kayeet.me\`\) \
    kayeet-game-server