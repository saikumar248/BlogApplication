#!/bin/bash

# Exit immediately if any command fails
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install Python packages from requirements.txt
pip install -r requirements.txt
