#!/bin/bash
# Build Windows .exe using Wine in Docker

echo "🍷 Building Windows .exe with Wine..."

# Start Xvfb for headless operation
Xvfb :99 -screen 0 1024x768x16 &
sleep 5

# Build the Windows executable
echo "🔨 Running PyInstaller..."
wine python -m PyInstaller --onefile --name "KKrasta-Keyworder.exe" kkrasta_keyworder.py

# Check if build was successful
if [ -f "dist/KKrasta-Keyworder.exe" ]; then
    echo "✅ Windows .exe built successfully!"
    ls -la dist/
else
    echo "❌ Build failed!"
    ls -la
fi

# Keep container running for debugging if needed
tail -f /dev/null
