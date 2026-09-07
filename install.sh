#!/usr/bin/env sh
set -eu
python3 "$(dirname "$0")/scripts/install.py"
echo "Copy config.example.toml to config.toml in the installed folder and add your keys."

