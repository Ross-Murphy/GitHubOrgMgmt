#!/bin/bash

read -p "GitHub Organization Name:" GITHUB_ORG_NAME
export GITHUB_ORG_NAME

read -s -p "GitHub Access Token:" GITHUB_PRIVATE_TOKEN
export GITHUB_PRIVATE_TOKEN

printf "\n" # Let's have a new line
