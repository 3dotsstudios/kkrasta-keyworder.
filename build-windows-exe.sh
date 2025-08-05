#!/bin/bash
# Build Windows .exe using Docker

echo "🚀 Building KKrasta Keyworder Windows .exe file..."
echo "📱 Created by @kktasta_ginx"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Create output directory
mkdir -p dist-windows

echo "🔨 Building Windows executable with Docker..."
echo "This may take a few minutes on first run..."

# Build and run the Windows container
docker-compose up --build windows-builder

# Check if build was successful
if [ -f "./dist-windows/KKrasta-Keyworder.exe" ]; then
    echo ""
    echo "✅ SUCCESS! Windows .exe file created:"
    echo "📁 Location: ./dist-windows/KKrasta-Keyworder.exe"
    echo "📊 Size: $(du -h ./dist-windows/KKrasta-Keyworder.exe | cut -f1)"
    echo ""
    echo "🎉 Your colorful KKrasta Keyworder is ready for Windows!"
    echo "📱 Created by @kktasta_ginx"
else
    echo ""
    echo "❌ Build failed! Check the Docker logs above for errors."
    echo "Common issues:"
    echo "  - Docker Desktop not running"
    echo "  - Windows containers not enabled"
    echo "  - Network connectivity issues"
fi

# Clean up containers
docker-compose down

echo ""
echo "🧹 Cleanup completed."
