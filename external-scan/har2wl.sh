#!/bin/bash

jq -r '.log.entries[].request.url' | grep cookie | grep -v \.js | grep -v \.css | grep -v \.svg | sort | uniq 
