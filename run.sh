#!/bin/bash


if ! command -v docker &> /dev/null
then
    echo "Docker is not istalled. Please install Docker to proceed."
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | awk '{print $3}' | sed 's/,//')
    USE_DOCKER_COMPOSE="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version | awk '{print $3}')
    USE_DOCKER_COMPOSE="docker compose"
else
    echo "Docker Compose is not installed. Please install Docker Compose to proceed."
    exit 1
fi

sudo $USE_DOCKER_COMPOSE up
