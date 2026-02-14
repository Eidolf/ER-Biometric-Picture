#!/bin/bash
# cleanup.sh - Removes dev environment, caches, and build artifacts

echo "Cleaning up project..."

# Remove Virtual Environment
if [ -d ".venv" ]; then
    echo "Removing .venv..."
    rm -rf .venv
fi

# Remove PyInstaller Artifacts
if [ -d "build" ]; then
    echo "Removing build/..."
    rm -rf build
fi
if [ -d "dist" ]; then
    echo "Removing dist/..."
    rm -rf dist
fi

# Remove Caches
echo "Removing __pycache__ and .pytest_cache..."
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
rm -rf .mypy_cache

# Remove Images? (Optional - keeping synthetic samples for now, removing output?)
# echo "Removing output images..."
# rm -rf output/*.jpg
# rm -rf output/*.json

echo "Cleanup complete. To restart, run installation commands again."
