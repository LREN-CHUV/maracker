#! /bin/bash

docker-compose -f stack-compose.yml up -d
docker-compose -f stack-compose.yml stop proxy
echo 'Wainting 50 seconds before restarting traefik'
sleep 40
docker-compose -f stack-compose.yml up -d proxy
echo "traefik restarted"
echo "marathon is accessible at marathon.localhost"
echo "chronos is accessible at chronos.localhost"
echo "traefik is accessible at traefik.localhost"
