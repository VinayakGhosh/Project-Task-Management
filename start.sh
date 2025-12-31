#!/bin/bash

set -e

echo "spinning up docker container to start database"
docker compose up -d

echo "starting uvicorn"
uvicorn main:app --reload