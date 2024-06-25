#!/bin/bash

# This script dumps env variables from serverless for the specified environment.
# See https://www.serverless.com/plugins/serverless-export-env for more details.

if [ $# -eq 0 ]; then
    echo "Error: Environment name not specified."
    echo "Usage: $0 <environment>"
    exit 1
fi

environment=$1

sls export-env -s $1

