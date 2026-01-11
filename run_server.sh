#!/bin/bash

# Function to run with native Ruby (rbenv)
run_native() {
    echo "Starting Jekyll with native Ruby (rbenv)..."
    rbenv exec bundle exec jekyll serve
}

# Function to run with Docker
run_docker() {
    echo "Starting Jekyll with Docker..."
    docker run --rm \
      --volume="$PWD:/srv/jekyll" \
      -p 4000:4000 \
      -it jekyll/jekyll:3.8 \
      jekyll serve
}

echo "How would you like to start the server?"
echo "1) Native Ruby (rbenv)"
echo "2) Docker (Recommended if native fails)"
read -p "Choose an option [1-2]: " choice

case $choice in
    1) run_native ;;
    2) run_docker ;;
    *) echo "Invalid option"; exit 1 ;;
esac