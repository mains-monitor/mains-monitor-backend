#!/bin/bash

# This script sources env variables for the specified environment.
# Need to be used before deployment.

if [ $# -eq 0 ]; then
    echo "Error: Environment name not specified."
    echo "Usage: source $0 <environment>"
    exit 1
fi

environment=$1

export $(grep -v '^#' .env-common | xargs -d '\n')
export $(grep -v '^#' .env-$environment | xargs -d '\n')