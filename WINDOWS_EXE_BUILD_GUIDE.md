# 🪟 Windows .exe Build Guide

**KKrasta Keyworder - Windows Executable Creation**  
📱 **Created by @kktasta_ginx**

## 🎯 Overview

This guide provides multiple methods to build a Windows .exe file from your colorful KKrasta Keyworder application.

## 🚀 Method 1: GitHub Actions (Recommended)

**✅ Easiest and most reliable method**

### Steps:
1. **Push to GitHub**: Upload your code to a GitHub repository
2. **Automatic Build**: The GitHub Action will automatically build the Windows .exe
3. **Download**: Get the .exe from the "Actions" tab or "Releases" section

### Setup:
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Add colorful KKrasta Keyworder with Windows build"

# Push to GitHub
git remote add origin https://github.com/yourusername/kkrasta-keyworder.git
git push -u origin main
```

### Result:
- Automatic .exe creation on every push
- Available in GitHub Actions artifacts
- Automatic releases with download links

---

## 🐳 Method 2: Docker with Wine

**✅ Works on macOS/Linux to create Windows .exe**

### Prerequisites:
- Docker Desktop installed and running

### Steps:
```bash
# Build the Docker image
docker build -f Dockerfile.wine -t kkrasta-wine-builder .

# Run the container to build .exe
docker run -v $(pwd)/dist-windows:/app/dist kkrasta-wine-builder

# Your .exe will be in ./dist-windows/
```

---

## 🪟 Method 3: Native Windows Build

**✅ If you have access to a Windows machine**

### Prerequisites:
- Windows 10/11
- Python 3.9+ installed

### Steps:
```cmd
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build the executable
pyinstaller --onefile --name "KKrasta-Keyworder.exe" kkrasta_keyworder.py

# Your .exe will be in ./dist/
```

---

## 🎨 Features of the Windows .exe

### ✨ Visual Features:
- **🌈 Colorful ASCII Banner**: Changes colors randomly every launch
- **📱 Telegram Handle**: "@kktasta_ginx" prominently displayed
- **🎯 Colorful Interface**: All menus and outputs use vibrant colors
- **💡 Keyword Highlighting**: Found keywords display with random colors

### 🔧 Functionality:
- **🔍 Multi-Engine Support**: Google, YouTube, Bing, Amazon, Yahoo, eBay, DuckDuckGo
- **⚡ Multi-Threading**: Fast concurrent scraping
- **💾 File Export**: Save keywords to text files
- **🔒 Proxy Support**: HTTPS and SOCKS5 proxy rotation
- **📊 Real-time Progress**: Live colorful status updates

---

## 📁 Expected Output

After building, you'll have:
- **`KKrasta-Keyworder.exe`** - Main Windows executable (~15-25MB)
- **No dependencies required** - Completely standalone
- **Double-click to run** - No installation needed

---

## 🎪 Usage on Windows

1. **Download/Build** the .exe file
2. **Double-click** `KKrasta-Keyworder.exe`
3. **Enjoy** the colorful ASCII art banner
4. **Select engines** using arrow keys and spacebar
5. **Configure settings** as needed
6. **Enter keywords** and watch the magic happen!

---

## 🐛 Troubleshooting

### Common Issues:

**❌ "Windows protected your PC" warning:**
- Click "More info" → "Run anyway"
- This is normal for unsigned executables

**❌ Antivirus false positive:**
- Add .exe to antivirus exclusions
- Common with PyInstaller executables

**❌ Build fails in Docker:**
- Ensure Docker Desktop is running
- Try the GitHub Actions method instead

**❌ Missing dependencies:**
- All dependencies are bundled in the .exe
- No separate installation needed

---

## 🎉 Distribution

Your Windows .exe is ready for:
- **📤 Direct sharing** - Send the .exe file to anyone
- **💿 USB distribution** - Copy to flash drives
- **🌐 Web download** - Host on your website
- **📱 Social sharing** - Share with your Telegram followers!

---

## 🏆 Recommended Approach

**For best results, use GitHub Actions:**
1. ✅ Automatic building
2. ✅ Professional releases
3. ✅ Download statistics
4. ✅ Version management
5. ✅ No local setup required

---

**🎨 Built with love and colors by @kktasta_ginx**
