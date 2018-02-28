#!/bin/bash

path="$(cd "../../Schema/$(dirname "$1")"; pwd)/$(basename "$1")"

pykwalify -d "${path}" -s schema.yml
