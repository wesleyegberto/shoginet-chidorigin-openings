#!/bin/bash
# Convenience script to run GitHub Pages server locally

echo "Starting local Shogi Tactics web server..."
echo "Access at: http://localhost:8080"
echo "Press Ctrl+C to stop."

python3 -m http.server 8080 -d pages
