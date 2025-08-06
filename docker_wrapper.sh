#!/bin/bash
# Docker wrapper script to handle permissions

if command -v docker >/dev/null 2>&1; then
    sudo docker "$@"
else
    echo "Docker not found!"
    exit 1
fi
