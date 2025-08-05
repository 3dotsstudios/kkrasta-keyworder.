# KKrasta Keyworder - Advanced Keyword Research Tool

A robust CLI-based keyword research tool that scrapes autosuggestions and related keywords from multiple search engines including Google, YouTube, Bing, Amazon, Yahoo, eBay, and DuckDuckGo.

## Features

- 🔍 **Multiple Search Engines**: Support for 8 different search engines
- 📁 **File Input Support**: Load keywords from text files or enter manually
- ✨ **Clean Output Format**: Results without timestamps or source information
- 🌐 **Proxy Support**: HTTP and SOCKS5 proxy rotation
- 🧅 **Tor Integration**: Anonymous scraping via Tor network
- ⚡ **Multi-threading**: Concurrent scraping for faster results
- 💾 **File Export**: Save results to text files
- 🎨 **Colorized Output**: Beautiful terminal interface with colors
- 🛡️ **Error Handling**: Robust error handling and retry mechanisms
- 🔧 **Configurable**: Customizable settings for threads, timeouts, and limits

## Requirements

- Python 3.6 or higher
- Internet connection
- Optional: Tor (for anonymous scraping)

## Installation

1. **Clone or download the repository**
   ```bash
   cd keyworder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Install Tor (for anonymous scraping)**
   - **macOS**: `brew install tor`
   - **Ubuntu/Debian**: `sudo apt-get install tor`
   - **Windows**: Download from [Tor Project](https://www.torproject.org/)

## Quick Start

1. **Run the application**
   ```bash
   python kkrasta_keyworder.py
   ```

2. **Follow the interactive prompts**:
   - Select search engines to scrape
   - Configure proxy settings (optional)
   - Set scraping parameters
   - Choose input method (manual or file)
   - Enter seed keywords or load from file

3. **Monitor the results** in real-time and find them saved in your output file

## Usage Examples

### Basic Usage
```bash
python kkrasta_keyworder.py
```
Then follow the interactive menu to:
- Select "Google" and "YouTube"
- Skip proxy configuration
- Use default settings
- Choose "Type keywords manually"
- Enter "python programming" as seed keyword

### With File Input
1. Create a `keywords.txt` file with one keyword per line:
   ```
   python programming
   web development
   machine learning
   data science
   artificial intelligence
   ```

2. Run the application and select "Load from file" when prompted

### With Proxy Support
1. Create a `proxies.txt` file with one proxy per line:
   ```
   http://proxy1:port
   http://proxy2:port
   socks5://proxy3:port
   ```

2. Run the application and select proxy configuration when prompted

### With Tor (Anonymous)
1. Start Tor service:
   ```bash
   # macOS/Linux
   tor
   
   # Or as service
   sudo systemctl start tor
   ```

2. Run the application and select "DuckDuckGo (via Tor)"

## Input Methods

### Manual Entry
Enter keywords separated by commas:
```
python programming, web development, machine learning
```

### File Input
Create a text file with one keyword per line:
```
python programming
web development
machine learning
data science
artificial intelligence
```

Then select "Load from file" and provide the file path.

## Configuration Options

### Search Engines
- **Google**: Fast and comprehensive suggestions
- **YouTube**: Video-focused keywords
- **Bing**: Microsoft's search suggestions
- **Amazon**: Product-related keywords
- **Yahoo**: Alternative search suggestions
- **eBay**: E-commerce keywords
- **DuckDuckGo**: Privacy-focused suggestions
- **DuckDuckGo (Tor)**: Anonymous suggestions via Tor

### Scraping Settings
- **Max Threads**: Number of concurrent workers (default: 5)
- **Timeout**: Request timeout in seconds (default: 10)
- **Max Retries**: Number of retry attempts (default: 3)
- **Delay**: Delay between requests in seconds (default: 1.0)
- **Max Keywords**: Maximum keywords per engine (default: 1000)

### Proxy Settings
- **HTTP Proxies**: Standard HTTP/HTTPS proxies
- **SOCKS5 Proxies**: SOCKS5 proxy support
- **Proxy Rotation**: Automatic rotation through proxy list

## Output Format

Results are displayed in real-time with clean format:
```
💡 python programming tutorial
💡 python programming for beginners
💡 python programming course
💡 python programming projects
```

And optionally saved to a text file with one keyword per line (no timestamps or metadata):
```
python programming tutorial
python programming for beginners
python programming course
python programming projects
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Tor Connection Failed**
   - Ensure Tor is running: `tor` or `sudo systemctl start tor`
   - Check Tor control port (default: 9051)
   - Verify Tor SOCKS port (default: 9050)

3. **Proxy Errors**
   - Verify proxy format: `http://ip:port` or `socks5://ip:port`
   - Test proxy connectivity
   - Check proxy authentication if required

4. **Rate Limiting**
   - Increase delay between requests
   - Reduce number of threads
   - Use proxies or Tor for IP rotation

5. **No Results**
   - Try different seed keywords
   - Check internet connection
   - Verify search engine accessibility

### Error Messages

- **"stem not available"**: Install with `pip install stem`
- **"questionary is required"**: Install with `pip install questionary`
- **"Failed to connect to Tor"**: Start Tor service
- **"Proxy file not found"**: Create proxy file or skip proxy configuration

## Advanced Usage

### Custom Configuration
You can modify the default settings in the code:

```python
# In kkrasta_keyworder.py
@dataclass
class ScrapingConfig:
    max_threads: int = 10        # Increase threads
    timeout: int = 15            # Longer timeout
    delay_between_requests: float = 0.5  # Faster scraping
```

### Batch Processing
For automated runs, you can modify the interactive prompts or create a wrapper script.

### API Integration
The search engine clients can be used independently:

```python
from kkrasta_keyworder import GoogleClient, SearchEngine, ProxyConfig, ScrapingConfig

proxy_config = ProxyConfig()
scraping_config = ScrapingConfig()
client = GoogleClient(SearchEngine.GOOGLE, proxy_config, scraping_config)

suggestions = client.get_suggestions("your keyword")
print(suggestions)
```

## Performance Tips

1. **Optimize Thread Count**: Start with 5 threads, adjust based on your system
2. **Use Proxies**: Rotate IP addresses to avoid rate limiting
3. **Adjust Delays**: Balance speed vs. respectful scraping
4. **Monitor Resources**: Watch CPU and memory usage
5. **Filter Results**: Remove duplicates and irrelevant keywords

## Legal and Ethical Considerations

- ⚖️ **Respect Terms of Service**: Each search engine has usage policies
- 🤝 **Rate Limiting**: Don't overwhelm servers with requests
- 🔒 **Privacy**: Use Tor for anonymous research when needed
- 📊 **Research Purpose**: Use for legitimate keyword research only

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the terms of service of the search engines you're scraping.

## Support

If you encounter issues:

1. Check the log file: `kkrasta_keyworder.log`
2. Verify dependencies: `pip list`
3. Update packages: `pip install -r requirements.txt --upgrade`

## Changelog

### Version 3.0 (KKrasta Keyworder)
- ✅ Renamed to KKrasta Keyworder
- ✅ Added file input support for keywords
- ✅ Clean output format (no timestamps/source info)
- ✅ Improved user interface
- ✅ Enhanced error handling
- ✅ Comprehensive testing suite
- ✅ Performance optimizations
- ✅ Thread safety improvements

---

**Happy Keyword Research! 🚀**
