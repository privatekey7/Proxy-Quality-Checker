import requests
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


PIXELSCAN_URL = "https://212133867.extension.pixelscan.net/#212133867"

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    GRAY = '\033[90m'
    LIGHT_BLUE = '\033[94m'
    ORANGE = '\033[38;5;208m'


def print_banner():
    """Prints a beautiful ANSI banner"""
    # Set UTF-8 encoding for Windows console
    if os.name == 'nt':
        try:
            import sys
            if sys.stdout.encoding != 'utf-8':
                sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
  ██████╗ ██████╗  ██████╗ ██╗  ██╗ ██╗    ██╗
  ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝ ██║    ██║
  ██████╔╝██████╔╝██║   ██║ ╚███╔╝   ║██████║
  ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗     ║██║
  ██║     ██║  ██║╚██████╔╝██╔╝ ██╗    ║██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝    ╚══╝
{Colors.RESET}
{Colors.YELLOW}  ██████╗ ██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
  ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Colors.RESET}
{Colors.GRAY}{'='*63}{Colors.RESET}
{Colors.GRAY}Telegram Channel: {Colors.LIGHT_BLUE}https://t.me/privatekey7{Colors.RESET}
{Colors.GRAY}{'='*63}{Colors.RESET}
"""
    print(banner)


def parse_proxy(proxy_str: str):
    ip, port, user, password = proxy_str.strip().split(":")
    return ip, port, user, password


def check_proxy(proxy_str: str):
    ip, port, user, password = parse_proxy(proxy_str)

    # Прокси в формате для requests с авторизацией в URL
    proxy_url = f"http://{user}:{password}@{ip}:{port}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
    }

    try:
        resp = requests.get(
            PIXELSCAN_URL,
            headers=headers,
            proxies=proxies,
            timeout=15,
        )
        resp.raise_for_status()
        
        # Парсим JSON ответ и извлекаем качество
        try:
            data = resp.json()
            quality = data.get("quality", "unknown")
            return {
                "proxy": proxy_str,
                "status": "working",
                "quality": quality,
                "ip": ip,
                "port": port
            }
        except json.JSONDecodeError:
            # Если ответ не JSON, считаем прокси рабочим, но качество unknown
            return {
                "proxy": proxy_str,
                "status": "working",
                "quality": "unknown",
                "ip": ip,
                "port": port
            }
    except Exception as e:
        return {
            "proxy": proxy_str,
            "status": "not_working",
            "quality": None,
            "ip": ip,
            "port": port,
            "error": str(e)
        }


def load_proxies_from_file(filename: str = "proxy.txt"):
    """Loads proxies from a file (one per line)"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except FileNotFoundError:
        print(f"File {filename} not found!")
        return []
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []


def save_results(results):
    """Saves check results into files grouped by quality"""
    # Create results folder if missing
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    high_proxies = []
    medium_proxies = []
    low_proxies = []
    not_working_proxies = []
    
    for result in results:
        if result["status"] == "not_working":
            not_working_proxies.append(result["proxy"])
        elif result["quality"] == "high":
            high_proxies.append(result["proxy"])
        elif result["quality"] == "medium":
            medium_proxies.append(result["proxy"])
        elif result["quality"] == "low":
            low_proxies.append(result["proxy"])
    
    # Save working proxies by quality
    if high_proxies:
        filepath = os.path.join(results_dir, "high_quality_proxies.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(high_proxies))
    
    if medium_proxies:
        filepath = os.path.join(results_dir, "medium_quality_proxies.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(medium_proxies))
    
    if low_proxies:
        filepath = os.path.join(results_dir, "low_quality_proxies.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(low_proxies))
    
    # Save non-working proxies
    if not_working_proxies:
        filepath = os.path.join(results_dir, "not_working_proxies.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(not_working_proxies))
    
    # Stats
    total_working = len(high_proxies) + len(medium_proxies) + len(low_proxies)
    print(f"\n📊 Stats:")
    print(f"   Working: {total_working} (high: {len(high_proxies)}, medium: {len(medium_proxies)}, low: {len(low_proxies)})")
    print(f"   Dead: {len(not_working_proxies)}")
    print(f"   Total: {len(results)}")


def check_proxies_batch(proxies_batch, pbar):
    """Checks a batch of proxies in parallel"""
    results = []
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Запускаем проверку всех прокси в батче параллельно
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies_batch}
        
        for future in as_completed(future_to_proxy):
            result = future.result()
            results.append(result)
            pbar.update(1)
    
    return results


if __name__ == "__main__":
    # Clear screen and print banner
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    proxies = load_proxies_from_file("proxy.txt")
    
    if not proxies:
        print("proxy.txt is empty or has no valid proxies!")
    else:
        print(f"Found {len(proxies)} proxies to check\n")
        
        # Split proxies into batches of 50
        batch_size = 50
        batches = [proxies[i:i + batch_size] for i in range(0, len(proxies), batch_size)]
        
        all_results = []
        
        # Progress bar
        with tqdm(total=len(proxies), desc="Checking proxies", bar_format='{desc}: {bar} {n_fmt}/{total_fmt}', unit="proxy", ncols=100) as pbar:
            for batch in batches:
                batch_results = check_proxies_batch(batch, pbar)
                all_results.extend(batch_results)
        
        # Save results
        print("\n" + "="*50)
        save_results(all_results)
