#!/usr/bin/env python3
"""
KKrasta Keyworder - Advanced CLI-based keyword research tool
A robust scraper for autosuggestions and related keywords from multiple search engines.
"""

import asyncio
import json
import random
import re
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from queue import Queue, Empty
from threading import Lock, Event
from typing import Dict, List, Optional, Set, Tuple, Union, Generator
from urllib.parse import quote_plus, urljoin
import logging

# Third-party imports with error handling
try:
    import questionary
except ImportError as e:
    print(f"Error: questionary is required. Install with: pip install questionary")
    sys.exit(1)

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError as e:
    print(f"Error: requests and urllib3 are required. Install with: pip install requests urllib3")
    sys.exit(1)

try:
    import stem
    from stem import Signal
    from stem.control import Controller
    STEM_AVAILABLE = True
except ImportError:
    print("Warning: stem not available. Tor functionality will be disabled.")
    STEM_AVAILABLE = False
    Controller = None
    Signal = None

# Optional imports
try:
    import colorama
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color constants
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kkrasta_keyworder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_random_colors():
    """Get random color combinations for the ASCII banner."""
    colors = [
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, 
        Fore.MAGENTA, Fore.CYAN, Fore.WHITE
    ]
    styles = [Style.BRIGHT, Style.NORMAL]
    
    # Return different colors for different parts
    return {
        'primary': random.choice(colors) + random.choice(styles),
        'secondary': random.choice(colors) + random.choice(styles),
        'accent': random.choice(colors) + Style.BRIGHT,
        'telegram': Fore.MAGENTA + Style.BRIGHT,
        'reset': Style.RESET_ALL
    }

def display_colorful_banner():
    """Display the colorful ASCII banner with random colors."""
    colors = get_random_colors()
    
    # First part of ASCII art (KKRASTA)
    kkrasta_art = f"""{colors['primary']}
██╗  ██╗██╗  ██╗██████╗  █████╗ ███████╗████████╗ █████╗ 
██║ ██╔╝██║ ██╔╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔══██╗
█████╔╝ █████╔╝ ██████╔╝███████║███████╗   ██║   ███████║
██╔═██╗ ██╔═██╗ ██╔══██╗██╔══██║╚════██║   ██║   ██╔══██║
██║  ██╗██║  ██╗██║  ██║██║  ██║███████║   ██║   ██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝{colors['reset']}"""

    # Second part of ASCII art (KEYWORDER)
    keyworder_art = f"""{colors['secondary']}
██╗  ██╗███████╗██╗   ██╗██╗    ██╗ ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
██║ ██╔╝██╔════╝╚██╗ ██╔╝██║    ██║██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
█████╔╝ █████╗   ╚████╔╝ ██║ █╗ ██║██║   ██║██████╔╝██║  ██║█████╗  ██████╔╝
██╔═██╗ ██╔══╝    ╚██╔╝  ██║███╗██║██║   ██║██╔══██╗██║  ██║██╔══╝  ██╔══██╗
██║  ██╗███████╗   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║
╚═╝  ╚═╝╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝{colors['reset']}"""
    
    # Telegram handle and description
    telegram_section = f"""
{colors['accent']}🔍 Advanced Keyword Research Tool{colors['reset']}
{colors['telegram']}📱 Created by @kktasta_ginx{colors['reset']}
{colors['accent']}{"=" * 80}{colors['reset']}"""
    
    # Print the complete banner
    print(kkrasta_art)
    print(keyworder_art)
    print(telegram_section)

def get_colorful_style():
    """Get colorful styling for questionary prompts."""
    colors = get_random_colors()
    return {
        'question': colors['accent'],
        'answer': colors['primary'],
        'pointer': colors['secondary'] + '❯',
        'highlighted': colors['accent'],
        'selected': colors['primary'],
        'instruction': colors['secondary']
    }

# Python version compatibility
def random_choices(population, k=1):
    """Compatibility function for random.choices (Python 3.6+)"""
    if hasattr(random, 'choices'):
        return random.choices(population, k=k)
    else:
        # Fallback for older Python versions
        return [random.choice(population) for _ in range(k)]

class SearchEngine(Enum):
    """Enumeration of supported search engines."""
    GOOGLE = "Google"
    YOUTUBE = "YouTube"
    BING = "Bing"
    AMAZON = "Amazon"
    YAHOO = "Yahoo"
    EBAY = "eBay"
    DUCKDUCKGO = "DuckDuckGo (Clearnet)"
    DUCKDUCKGO_TOR = "DuckDuckGo (via Tor)"

class ProxyType(Enum):
    """Enumeration of supported proxy types."""
    HTTPS = "HTTPS"
    SOCKS5 = "SOCKS5"

@dataclass
class ProxyConfig:
    """Configuration for proxy settings."""
    enabled: bool = False
    proxy_type: Optional[ProxyType] = None
    proxies: List[str] = field(default_factory=list)
    current_proxy_index: int = 0

    def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy in rotation."""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    def validate(self) -> bool:
        """Validate proxy configuration."""
        if not self.enabled:
            return True
        
        if not self.proxy_type:
            logger.error("Proxy type must be specified when proxies are enabled")
            return False
        
        if not self.proxies:
            logger.error("No proxies provided")
            return False
        
        return True

@dataclass
class ScrapingConfig:
    """Configuration for scraping behavior."""
    max_threads: int = 5
    timeout: int = 10
    max_retries: int = 3
    delay_between_requests: float = 1.0
    max_keywords_per_engine: int = 1000
    save_to_file: bool = True
    output_filename: str = "keywords_output.txt"

    def validate(self) -> bool:
        """Validate scraping configuration."""
        if self.max_threads < 1:
            logger.error("max_threads must be at least 1")
            return False
        
        if self.timeout < 1:
            logger.error("timeout must be at least 1 second")
            return False
        
        if self.max_retries < 0:
            logger.error("max_retries cannot be negative")
            return False
        
        if self.delay_between_requests < 0:
            logger.error("delay_between_requests cannot be negative")
            return False
        
        if self.max_keywords_per_engine < 1:
            logger.error("max_keywords_per_engine must be at least 1")
            return False
        
        return True

class TorManager:
    """Manages Tor connections and identity changes."""

    def __init__(self, control_port: int = 9051, socks_port: int = 9050):
        if not STEM_AVAILABLE:
            raise ImportError("stem library is required for Tor functionality")
        
        self.control_port = control_port
        self.socks_port = socks_port
        self.controller: Optional[Controller] = None
        self._lock = Lock()

    def connect(self) -> bool:
        """Connect to Tor control port."""
        try:
            self.controller = Controller.from_port(port=self.control_port)
            self.controller.authenticate()
            logger.info("Connected to Tor successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Tor: {e}")
            return False

    def new_identity(self) -> bool:
        """Request a new Tor identity."""
        with self._lock:
            try:
                if self.controller:
                    self.controller.signal(Signal.NEWNYM)
                    time.sleep(2)  # Wait for new circuit
                    logger.info("Tor identity changed")
                    return True
            except Exception as e:
                logger.error(f"Failed to change Tor identity: {e}")
        return False

    def get_proxy_dict(self) -> Dict[str, str]:
        """Get proxy configuration for requests."""
        return {
            'http': f'socks5://127.0.0.1:{self.socks_port}',
            'https': f'socks5://127.0.0.1:{self.socks_port}'
        }

    def close(self):
        """Close Tor controller connection."""
        if self.controller:
            try:
                self.controller.close()
            except Exception as e:
                logger.error(f"Error closing Tor controller: {e}")

class SearchEngineClient:
    """Base class for search engine clients."""

    def __init__(self, engine: SearchEngine, proxy_config: ProxyConfig, 
                 scraping_config: ScrapingConfig, tor_manager: Optional[TorManager] = None):
        self.engine = engine
        self.proxy_config = proxy_config
        self.scraping_config = scraping_config
        self.tor_manager = tor_manager
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a configured requests session."""
        session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=self.scraping_config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent
        session.headers.update({
            'User-Agent': self._get_random_user_agent()
        })
        
        return session

    def _get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        return random.choice(user_agents)

    def _get_proxies(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration for requests."""
        if self.engine == SearchEngine.DUCKDUCKGO_TOR and self.tor_manager:
            return self.tor_manager.get_proxy_dict()
        
        if not self.proxy_config.enabled:
            return None
        
        proxy = self.proxy_config.get_next_proxy()
        if not proxy:
            return None
        
        if self.proxy_config.proxy_type == ProxyType.HTTPS:
            return {'http': proxy, 'https': proxy}
        elif self.proxy_config.proxy_type == ProxyType.SOCKS5:
            return {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
        
        return None

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get keyword suggestions for the given keyword."""
        raise NotImplementedError("Subclasses must implement get_suggestions")

    def _validate_keyword(self, keyword: str) -> bool:
        """Validate keyword input."""
        if not keyword or not keyword.strip():
            return False
        if len(keyword.strip()) > 200:  # Reasonable limit
            return False
        return True

class GoogleClient(SearchEngineClient):
    """Client for Google autosuggestions."""

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get Google autosuggestions."""
        if not self._validate_keyword(keyword):
            return []
        
        try:
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'chrome',
                'q': keyword.strip(),
                'hl': 'en'
            }
            
            response = self.session.get(
                url, 
                params=params, 
                proxies=self._get_proxies(),
                timeout=self.scraping_config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                suggestions = [suggestion for suggestion in data[1] 
                             if suggestion != keyword and isinstance(suggestion, str)]
                return suggestions[:20]  # Limit results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Google suggestions for '{keyword}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for Google suggestions '{keyword}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting Google suggestions for '{keyword}': {e}")
        
        return []

class YouTubeClient(SearchEngineClient):
    """Client for YouTube autosuggestions."""

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get YouTube autosuggestions."""
        if not self._validate_keyword(keyword):
            return []
        
        try:
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'youtube',
                'ds': 'yt',
                'q': keyword.strip(),
                'hl': 'en'
            }
            
            response = self.session.get(
                url, 
                params=params, 
                proxies=self._get_proxies(),
                timeout=self.scraping_config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                suggestions = [suggestion for suggestion in data[1] 
                             if suggestion != keyword and isinstance(suggestion, str)]
                return suggestions[:20]  # Limit results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting YouTube suggestions for '{keyword}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for YouTube suggestions '{keyword}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting YouTube suggestions for '{keyword}': {e}")
        
        return []

class BingClient(SearchEngineClient):
    """Client for Bing autosuggestions."""

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get Bing autosuggestions."""
        if not self._validate_keyword(keyword):
            return []
        
        try:
            url = "https://www.bing.com/AS/Suggestions"
            params = {
                'pt': 'page.serp',
                'mkt': 'en-us',
                'qry': keyword.strip(),
                'cp': len(keyword.strip()),
                'cvid': ''.join(random_choices(string.ascii_uppercase + string.digits, k=32))
            }
            
            response = self.session.get(
                url, 
                params=params, 
                proxies=self._get_proxies(),
                timeout=self.scraping_config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            suggestions = []
            
            if 'AS' in data and 'Results' in data['AS']:
                for result in data['AS']['Results']:
                    if 'Suggests' in result:
                        for suggest in result['Suggests']:
                            if 'Txt' in suggest and suggest['Txt'] != keyword:
                                suggestions.append(suggest['Txt'])
            
            return suggestions[:20]  # Limit results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Bing suggestions for '{keyword}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for Bing suggestions '{keyword}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting Bing suggestions for '{keyword}': {e}")
        
        return []

class AmazonClient(SearchEngineClient):
    """Client for Amazon autosuggestions."""

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get Amazon autosuggestions."""
        if not self._validate_keyword(keyword):
            return []
        
        try:
            url = "https://completion.amazon.com/api/2017/suggestions"
            params = {
                'mid': 'ATVPDKIKX0DER',
                'alias': 'aps',
                'site-variant': 'desktop',
                'version': '3',
                'event': 'onkeypress',
                'wc': '',
                'lop': 'en_US',
                'last-word': '',
                'prefix': keyword.strip(),
                'src': 'completion',
                'client': 'amazon-search-ui'
            }
            
            response = self.session.get(
                url, 
                params=params, 
                proxies=self._get_proxies(),
                timeout=self.scraping_config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            suggestions = []
            
            if 'suggestions' in data:
                for suggestion in data['suggestions']:
                    if 'value' in suggestion and suggestion['value'] != keyword:
                        suggestions.append(suggestion['value'])
            
            return suggestions[:20]  # Limit results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Amazon suggestions for '{keyword}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for Amazon suggestions '{keyword}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting Amazon suggestions for '{keyword}': {e}")
        
        return []

class YahooClient(SearchEngineClient):
    """Client for Yahoo autosuggestions."""

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get Yahoo autosuggestions."""
        if not self._validate_keyword(keyword):
            return []
        
        try:
            url = "https://search.yahoo.com/sugg/gossip/gossip-us-ura"
            params = {
                'output': 'sd1',
                'command': keyword.strip(),
                'nresults': '10'
            }
            
            response = self.session.get(
                url, 
                params=params, 
                proxies=self._get_proxies(),
                timeout=self.scraping_config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            suggestions = []
            
            if 'r' in data:
                for item in data['r']:
                    if 'k' in item and item['k'] != keyword:
                        suggestions.append(item['k'])
            
            return suggestions[:20]  # Limit results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Yahoo suggestions for '{keyword}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for Yahoo suggestions '{keyword}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting Yahoo suggestions for '{keyword}': {e}")
        
        return []

class EbayClient(SearchEngineClient):
    """Client for eBay autosuggestions."""

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get eBay autosuggestions."""
        if not self._validate_keyword(keyword):
            return []
        
        try:
            # Use eBay's autocomplete API endpoint
            url = "https://www.ebay.com/sch/i.html"
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest'
            }
            params = {
                '_nkw': keyword.strip(),
                '_sacat': '0',
                'LH_Complete': '1',
                'rt': 'nc'
            }
            
            response = self.session.get(
                url, 
                params=params, 
                headers=headers,
                proxies=self._get_proxies(),
                timeout=self.scraping_config.timeout
            )
            response.raise_for_status()
            
            # Try to extract suggestions from the HTML response
            suggestions = []
            # Look for related searches in the response
            pattern = r'data-testid="srp-related-searches"[^>]*>.*?<a[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, response.text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                clean_suggestion = re.sub(r'<[^>]+>', '', match).strip()
                if clean_suggestion and clean_suggestion != keyword:
                    suggestions.append(clean_suggestion)
            
            return suggestions[:10]  # Limit to 10 suggestions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting eBay suggestions for '{keyword}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting eBay suggestions for '{keyword}': {e}")
        
        return []

class DuckDuckGoClient(SearchEngineClient):
    """Client for DuckDuckGo autosuggestions."""

    def get_suggestions(self, keyword: str) -> List[str]:
        """Get DuckDuckGo autosuggestions."""
        if not self._validate_keyword(keyword):
            return []
        
        try:
            url = "https://duckduckgo.com/ac/"
            params = {
                'q': keyword.strip(),
                'type': 'list'
            }
            
            # Handle Tor identity change if using Tor
            if self.engine == SearchEngine.DUCKDUCKGO_TOR and self.tor_manager:
                # Occasionally change Tor identity
                if random.random() < 0.1:  # 10% chance
                    self.tor_manager.new_identity()
            
            response = self.session.get(
                url, 
                params=params, 
                proxies=self._get_proxies(),
                timeout=self.scraping_config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            suggestions = []
            
            # DuckDuckGo returns a list where the first element is the query
            # and subsequent elements are suggestion objects
            if isinstance(data, list) and len(data) > 1:
                for item in data[1:]:
                    if isinstance(item, dict) and 'phrase' in item:
                        phrase = item['phrase']
                        if phrase != keyword:
                            suggestions.append(phrase)
                    elif isinstance(item, str) and item != keyword:
                        suggestions.append(item)
            
            return suggestions[:20]  # Limit results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting DuckDuckGo suggestions for '{keyword}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for DuckDuckGo suggestions '{keyword}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting DuckDuckGo suggestions for '{keyword}': {e}")
        
        return []

class KeywordSheeter:
    """Main keyword sheeter application."""

    def __init__(self):
        self.selected_engines: List[SearchEngine] = []
        self.proxy_config = ProxyConfig()
        self.scraping_config = ScrapingConfig()
        self.tor_manager: Optional[TorManager] = None
        self.clients: Dict[SearchEngine, SearchEngineClient] = {}
        self.scraped_keywords: Set[str] = set()
        self.keyword_queue = Queue()
        self.results_lock = Lock()
        self.stop_event = Event()
        self.output_file: Optional[Path] = None

    def setup_interactive_menu(self):
        """Set up the interactive CLI menu."""
        # Display the colorful banner
        display_colorful_banner()
        
        # Select search engines
        self._select_search_engines()
        
        # Configure proxy settings
        self._configure_proxy_settings()
        
        # Configure scraping settings
        self._configure_scraping_settings()
        
        # Validate configurations
        if not self._validate_configurations():
            print(f"{Fore.RED}❌ Configuration validation failed. Exiting.{Style.RESET_ALL}")
            sys.exit(1)
        
        # Initialize clients
        self._initialize_clients()

    def _validate_configurations(self) -> bool:
        """Validate all configurations."""
        if not self.proxy_config.validate():
            return False
        if not self.scraping_config.validate():
            return False
        return True

    def _select_search_engines(self):
        """Interactive search engine selection."""
        choices = []
        for engine in SearchEngine:
            if engine == SearchEngine.DUCKDUCKGO_TOR and not STEM_AVAILABLE:
                choices.append(f"{engine.value} (Disabled - stem not available)")
            else:
                choices.append(engine.value)
        
        try:
            print(f"{Fore.CYAN}(Use arrow keys to navigate, space to select, enter to confirm){Style.RESET_ALL}")
            selected = questionary.checkbox(
                f"{Fore.YELLOW}Select search engines to scrape:{Style.RESET_ALL}",
                choices=[choice for choice in choices if "Disabled" not in choice]
            ).ask()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
        
        if not selected:
            print(f"{Fore.RED}No search engines selected. Exiting.{Style.RESET_ALL}")
            sys.exit(1)
        
        # Convert selected strings back to enums
        self.selected_engines = [
            engine for engine in SearchEngine 
            if engine.value in selected
        ]
        
        print(f"{Fore.GREEN}✅ Selected engines: {', '.join([e.value for e in self.selected_engines])}{Style.RESET_ALL}")

    def _configure_proxy_settings(self):
        """Configure proxy settings."""
        try:
            use_proxy = questionary.confirm(
                f"{Fore.BLUE}Do you want to use proxies?{Style.RESET_ALL}"
            ).ask()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
        
        if use_proxy:
            self.proxy_config.enabled = True
            
            # Select proxy type
            try:
                proxy_type = questionary.select(
                    f"{Fore.BLUE}Select proxy type:{Style.RESET_ALL}",
                    choices=[pt.value for pt in ProxyType]
                ).ask()
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
            
            self.proxy_config.proxy_type = ProxyType(proxy_type)
            
            # Load proxy list
            try:
                proxy_file = questionary.path(
                    f"{Fore.BLUE}Path to proxy list file:{Style.RESET_ALL}",
                    default="list.txt"
                ).ask()
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
            
            try:
                with open(proxy_file, 'r') as f:
                    proxies = [line.strip() for line in f if line.strip()]
                
                if proxies:
                    self.proxy_config.proxies = proxies
                    print(f"{Fore.GREEN}✅ Loaded {len(proxies)} proxies{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️  No proxies found in file{Style.RESET_ALL}")
                    self.proxy_config.enabled = False
            
            except FileNotFoundError:
                print(f"{Fore.RED}❌ Proxy file '{proxy_file}' not found{Style.RESET_ALL}")
                self.proxy_config.enabled = False
            except Exception as e:
                print(f"{Fore.RED}❌ Error reading proxy file: {e}{Style.RESET_ALL}")
                self.proxy_config.enabled = False
        
        if SearchEngine.DUCKDUCKGO_TOR in self.selected_engines:
            if not STEM_AVAILABLE:
                print(f"{Fore.RED}❌ stem library not available. Removing Tor engine from selection.{Style.RESET_ALL}")
                self.selected_engines = [
                    e for e in self.selected_engines 
                    if e != SearchEngine.DUCKDUCKGO_TOR
                ]
            else:
                print(f"{Fore.BLUE}🧅 Tor configuration required for DuckDuckGo (Tor){Style.RESET_ALL}")
                try:
                    self.tor_manager = TorManager()
                    if not self.tor_manager.connect():
                        print(f"{Fore.RED}❌ Failed to connect to Tor. Make sure Tor is running.{Style.RESET_ALL}")
                        # Remove Tor engine from selection
                        self.selected_engines = [
                            e for e in self.selected_engines 
                            if e != SearchEngine.DUCKDUCKGO_TOR
                        ]
                except Exception as e:
                    print(f"{Fore.RED}❌ Error setting up Tor: {e}{Style.RESET_ALL}")
                    self.selected_engines = [
                        e for e in self.selected_engines 
                        if e != SearchEngine.DUCKDUCKGO_TOR
                    ]

    def _configure_scraping_settings(self):
        """Configure scraping behavior settings."""
        print(f"\n{Fore.CYAN}⚙️  Scraping Configuration{Style.RESET_ALL}")
        
        try:
            max_threads = questionary.text(
                f"{Fore.MAGENTA}Maximum concurrent threads:{Style.RESET_ALL}",
                default=str(self.scraping_config.max_threads),
                validate=lambda x: x.isdigit() and int(x) > 0
            ).ask()
            
            self.scraping_config.max_threads = int(max_threads)
        except (KeyboardInterrupt, ValueError):
            if KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
        
        try:
            save_file = questionary.confirm(
                f"{Fore.MAGENTA}Save results to file?{Style.RESET_ALL}",
                default=True
            ).ask()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
        
        self.scraping_config.save_to_file = save_file
        
        if save_file:
            try:
                filename = questionary.text(
                    f"{Fore.MAGENTA}Output filename:{Style.RESET_ALL}",
                    default=self.scraping_config.output_filename
                ).ask()
                self.scraping_config.output_filename = filename
                self.output_file = Path(filename)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                sys.exit(0)

    def _initialize_clients(self):
        """Initialize search engine clients."""
        client_classes = {
            SearchEngine.GOOGLE: GoogleClient,
            SearchEngine.YOUTUBE: YouTubeClient,
            SearchEngine.BING: BingClient,
            SearchEngine.AMAZON: AmazonClient,
            SearchEngine.YAHOO: YahooClient,
            SearchEngine.EBAY: EbayClient,
            SearchEngine.DUCKDUCKGO: DuckDuckGoClient,
            SearchEngine.DUCKDUCKGO_TOR: DuckDuckGoClient,
        }
        
        for engine in self.selected_engines:
            try:
                client_class = client_classes[engine]
                self.clients[engine] = client_class(
                    engine=engine,
                    proxy_config=self.proxy_config,
                    scraping_config=self.scraping_config,
                    tor_manager=self.tor_manager
                )
                logger.info(f"Initialized client for {engine.value}")
            except Exception as e:
                logger.error(f"Failed to initialize client for {engine.value}: {e}")

    def get_seed_keywords(self) -> List[str]:
        """Get initial seed keywords from user."""
        try:
            # Ask user to choose input method
            input_method = questionary.select(
                f"{Fore.GREEN}How would you like to provide seed keywords?{Style.RESET_ALL}",
                choices=[
                    "Type keywords manually",
                    "Load from file"
                ]
            ).ask()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
        
        keywords = []
        
        if input_method == "Type keywords manually":
            try:
                print(f"{Fore.CYAN}e.g., 'python programming, web development'{Style.RESET_ALL}")
                seed_input = questionary.text(
                    f"{Fore.GREEN}Enter seed keyword(s) (comma-separated):{Style.RESET_ALL}",
                    validate=lambda x: len(x.strip()) > 0
                ).ask()
                
                if seed_input:
                    keywords = [kw.strip() for kw in seed_input.split(',') if kw.strip()]
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
        
        elif input_method == "Load from file":
            try:
                file_path = questionary.path(
                    f"{Fore.GREEN}Enter path to keywords file (one keyword per line):{Style.RESET_ALL}",
                    validate=lambda x: len(x.strip()) > 0
                ).ask()
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        keywords = [line.strip() for line in f if line.strip()]
                    
                    if keywords:
                        print(f"{Fore.GREEN}✅ Loaded {len(keywords)} keywords from file{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️  No keywords found in file{Style.RESET_ALL}")
                        return []
                        
                except FileNotFoundError:
                    print(f"{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
                    return []
                except Exception as e:
                    print(f"{Fore.RED}❌ Error reading file: {e}{Style.RESET_ALL}")
                    return []
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
        
        # Validate keywords
        valid_keywords = []
        for keyword in keywords:
            if len(keyword) > 200:
                print(f"{Fore.YELLOW}⚠️  Keyword too long, skipping: {keyword[:50]}...{Style.RESET_ALL}")
                continue
            valid_keywords.append(keyword)
        
        return valid_keywords

    def scrape_keywords_worker(self, engine: SearchEngine):
        """Worker function for scraping keywords from a specific engine."""
        if engine not in self.clients:
            logger.error(f"No client available for {engine.value}")
            return
        
        client = self.clients[engine]
        scraped_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while (not self.stop_event.is_set() and 
               scraped_count < self.scraping_config.max_keywords_per_engine and
               consecutive_failures < max_consecutive_failures):
            try:
                try:
                    keyword = self.keyword_queue.get(timeout=5)
                except Empty:
                    # No more keywords in queue
                    break
                
                # Skip if already scraped
                with self.results_lock:
                    if keyword in self.scraped_keywords:
                        continue
                    self.scraped_keywords.add(keyword)
                
                print(f"{Fore.BLUE}🔍 [{engine.value}] Scraping: {keyword}{Style.RESET_ALL}")
                
                # Get suggestions
                suggestions = client.get_suggestions(keyword)
                
                if suggestions:
                    print(f"{Fore.GREEN}✅ [{engine.value}] Found {len(suggestions)} suggestions for '{keyword}'{Style.RESET_ALL}")
                    consecutive_failures = 0  # Reset failure counter
                    
                    # Add new keywords to queue and save results
                    with self.results_lock:
                        for suggestion in suggestions:
                            if suggestion not in self.scraped_keywords and len(suggestion.strip()) > 0:
                                self.keyword_queue.put(suggestion)
                                self._save_keyword(suggestion, engine.value)
                else:
                    print(f"{Fore.YELLOW}❌ [{engine.value}] No suggestions found for '{keyword}'{Style.RESET_ALL}")
                    consecutive_failures += 1
                
                scraped_count += 1
                
                # Respect rate limiting
                if self.scraping_config.delay_between_requests > 0:
                    time.sleep(self.scraping_config.delay_between_requests)
                
            except Exception as e:
                logger.error(f"Error in worker for {engine.value}: {e}")
                consecutive_failures += 1
                time.sleep(2)  # Wait before retrying
        
        if consecutive_failures >= max_consecutive_failures:
            logger.warning(f"Worker for {engine.value} stopped due to consecutive failures")

    def _save_keyword(self, keyword: str, source: str):
        """Save a keyword to file and display in terminal."""
        # Display in terminal with colorful output
        colors = get_random_colors()
        print(f"{colors['accent']}💡 {keyword}{colors['reset']}")
        
        # Save to file if enabled - just the keyword
        if self.scraping_config.save_to_file and self.output_file:
            try:
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(f"{keyword}\n")
            except Exception as e:
                logger.error(f"Error saving to file: {e}")

    def start_scraping(self):
        """Start the main scraping process."""
        seed_keywords = self.get_seed_keywords()
        
        if not seed_keywords:
            print(f"{Fore.RED}No seed keywords provided. Exiting.{Style.RESET_ALL}")
            return
        
        # Initialize output file
        if self.scraping_config.save_to_file and self.output_file:
            try:
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    f.write("")  # Start with empty file for clean keyword list
                print(f"{Fore.GREEN}📁 Output file initialized: {self.output_file}{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"Error initializing output file: {e}")
                print(f"{Fore.RED}❌ Failed to initialize output file{Style.RESET_ALL}")
        
        # Add seed keywords to queue
        for keyword in seed_keywords:
            self.keyword_queue.put(keyword)
        
        print(f"\n{Fore.CYAN}🚀 Starting keyword scraping with {len(self.selected_engines)} engines...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Max threads: {self.scraping_config.max_threads}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💾 Save to file: {self.scraping_config.save_to_file}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Press Ctrl+C to stop scraping...{Style.RESET_ALL}\n")
        
        # Start worker threads
        with ThreadPoolExecutor(max_workers=self.scraping_config.max_threads) as executor:
            try:
                # Submit workers for each engine
                futures = []
                for engine in self.selected_engines:
                    future = executor.submit(self.scrape_keywords_worker, engine)
                    futures.append(future)
                
                # Wait for completion or interruption
                while not all(f.done() for f in futures):
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}🛑 Stopping scraper...{Style.RESET_ALL}")
                self.stop_event.set()
                
                # Wait for threads to finish gracefully
                for future in futures:
                    try:
                        future.result(timeout=5)
                    except:
                        future.cancel()
        
        # Cleanup
        if self.tor_manager:
            self.tor_manager.close()
        
        print(f"\n{Fore.GREEN}✅ Scraping completed. Found {len(self.scraped_keywords)} unique keywords.{Style.RESET_ALL}")
        if self.output_file and self.scraping_config.save_to_file:
            print(f"{Fore.GREEN}📁 Results saved to: {self.output_file}{Style.RESET_ALL}")

def main():
    """Main application entry point."""
    try:
        # Check Python version
        if sys.version_info < (3, 6):
            print(f"{Fore.RED}❌ Python 3.6 or higher is required{Style.RESET_ALL}")
            sys.exit(1)
        
        app = KeywordSheeter()
        app.setup_interactive_menu()
        app.start_scraping()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"{Fore.RED}❌ An error occurred: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
