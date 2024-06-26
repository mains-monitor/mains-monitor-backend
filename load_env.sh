#!/bin/bash

if [ -e .env-common ]; then
    export $(grep -v '^#' .env-common | xargs -d '\n')
fi

if [ -e .env ]; then
    export $(grep -v '^#' .env | xargs -d '\n')
fi