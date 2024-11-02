#! bin/bash
COMPOSE_FILE="docker-compose-ver-2.yml"


## start a dummy container with snowplow-local-config volume, then remove dummy 
docker container create --name dummy -v snowplow-local-config:/snowplow-config hello-world
docker cp ./snowplow-config/. dummy:/snowplow-config/
docker rm dummy
docker-compose -f $COMPOSE_FILE up -d
docker-compose -f $COMPOSE_FILE run --rm snowplow-iglu-server setup --config //home/snowplow/snowplow-config/iglu-server.hocon