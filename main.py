from proxy_checker import ProxyChecker

def load_proxies(filename='proxy.txt'):
    proxies = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    ip, port, login, password = line.split(':')
                    proxies.append({
                        'ip': ip,
                        'port': port,
                        'login': login,
                        'password': password
                    })
                except ValueError:
                    print(f"Неверный формат прокси: {line}")
    return proxies

def main():
    checker = ProxyChecker()
    proxies = load_proxies('proxy.txt')
    
    try:
        results = checker.check_proxies(proxies)
        print(f"\nПроверено {len(proxies)} прокси")
    except Exception as e:
        print(f"Ошибка при проверке прокси: {e}")

if __name__ == "__main__":
    main() 