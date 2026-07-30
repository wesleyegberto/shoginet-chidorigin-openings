#!/bin/bash
# Convenience script to run GitHub Pages server locally

echo "Starting local Shogi Tactics web server..."
echo "Access at: http://localhost:9000"
echo "Press Ctrl+C to stop."

python3 -m http.server 9000 -d pages
