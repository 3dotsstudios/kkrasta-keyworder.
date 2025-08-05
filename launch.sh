#!/bin/bash
# KKrasta Keyworder Launcher
# Simple launcher script for the standalone app

echo "🚀 Launching KKrasta Keyworder..."
echo "📱 Created by @kktasta_ginx"
echo ""

# Check if the executable exists
if [ ! -f "./dist/KKrasta-Keyworder" ]; then
    echo "❌ Error: KKrasta-Keyworder executable not found!"
    echo "Please make sure the dist/KKrasta-Keyworder file exists."
    exit 1
fi

# Make sure it's executable
chmod +x ./dist/KKrasta-Keyworder

# Launch the app
./dist/KKrasta-Keyworder
