from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from colorama import init, Fore, Style
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
import logging
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class ProxyChecker:
    def __init__(self):
        self.extension_file = "proxy_checker-1.0.2.xpi"
        init()  # Инициализация colorama
        
        # Подавляем все технические сообщения
        logging.getLogger('selenium').setLevel(logging.ERROR)
        os.environ['WDM_LOG_LEVEL'] = '0'
        
    def test_proxy(self, proxy):
        """Проверка работоспособности прокси"""
        proxy_str = f"{proxy['ip']}:{proxy['port']}"
        proxy_auth = f"{proxy['login']}:{proxy['password']}"
        
        proxies = {
            'http': f'http://{proxy_auth}@{proxy_str}',
            'https': f'http://{proxy_auth}@{proxy_str}'
        }
        
        try:
            response = requests.get(
                'http://ip-api.com/json',
                proxies=proxies,
                timeout=10,
                verify=False
            )
            return True, proxy
        except Exception as e:
            return False, proxy
            
    def check_proxies(self, proxies):
        if not os.path.exists(self.extension_file):
            raise Exception(f"Расширение не найдено. Пожалуйста, скачайте {self.extension_file}")
            
        # Подавляем предупреждения о версии geckodriver
        import logging
        logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.ERROR)
        
        # Создаем папку results если её нет
        if not os.path.exists('results'):
            os.makedirs('results')
            
        # Очищаем старые файлы результатов
        for quality in ['high', 'medium', 'low', 'not_working']:
            with open(f'results/{quality}.txt', 'w', encoding='utf-8') as f:
                f.write('')
            
        print(f"{Fore.CYAN}Предварительная проверка {len(proxies)} прокси на работоспособность...{Style.RESET_ALL}")
        
        # Проверяем все прокси в многопоточном режиме
        working_proxies = []
        not_working = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for proxy in proxies:
                futures.append(executor.submit(self.test_proxy, proxy))
            
            # Создаем прогресс бар
            with tqdm(total=len(proxies), desc="Проверка прокси", unit="proxy") as pbar:
                for future in futures:
                    is_working, proxy = future.result()
                    if is_working:
                        working_proxies.append(proxy)
                    else:
                        not_working.append(f"{proxy['ip']}:{proxy['port']}:{proxy['login']}:{proxy['password']}")
                    pbar.update(1)
        
        # Сразу сохраняем нерабочие прокси
        with open('results/not_working.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(not_working))
        
        print(f"\n{Fore.GREEN}Рабочих прокси: {len(working_proxies)}{Style.RESET_ALL}")
        print(f"{Fore.RED}Нерабочих прокси: {len(not_working)}{Style.RESET_ALL}\n")
        
        # Продолжаем проверку только с рабочими прокси
        if not working_proxies:
            print(f"{Fore.RED}Нет рабочих прокси для проверки качества{Style.RESET_ALL}")
            return []
            
        # Словари для сортировки прокси по качеству (без not_working)
        quality_proxies = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Разбиваем список прокси на группы по 50
        proxy_groups = [working_proxies[i:i + 50] for i in range(0, len(working_proxies), 50)]
        total_groups = len(proxy_groups)
        
        print(f"{Fore.CYAN}Всего прокси: {len(working_proxies)}")
        print(f"Будет выполнено {total_groups} проверок по 50 прокси{Style.RESET_ALL}\n")
        
        MAX_RETRIES = 3  # Максимальное количество попыток для каждой группы
        driver = None
        all_results = []
        
        try:
            for group_index, proxy_group in enumerate(proxy_groups, 1):
                retry_count = 0
                success = False
                
                while not success and retry_count < MAX_RETRIES:
                    try:
                        if retry_count > 0:
                            print(f"{Fore.YELLOW}Повторная попытка {retry_count} из {MAX_RETRIES}{Style.RESET_ALL}")
                        
                        # Создаем новый браузер только при первом запуске или при ошибке
                        if driver is None or retry_count > 0:
                            if driver:
                                try:
                                    driver.quit()
                                except:
                                    pass
                                time.sleep(2)
                            
                            print(f"{Fore.YELLOW}Запуск нового браузера...{Style.RESET_ALL}")
                            options = Options()
                            options.set_preference('xpinstall.signatures.required', False)
                            driver = webdriver.Firefox(options=options)
                            
                            # Устанавливаем расширение
                            driver.get("about:debugging#/runtime/this-firefox")
                            time.sleep(3)
                            extension_path = os.path.abspath(self.extension_file)
                            extension_id = driver.install_addon(extension_path, temporary=True)
                            driver.refresh()
                            time.sleep(3)
                            extension_uuid = self._get_extension_uuid(driver)
                            self._open_extension_popup(driver, extension_uuid)
                            time.sleep(2)
                        else:
                            # Для последующих проверок нажимаем Run New Test
                            try:
                                run_new_test = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-1levzx2'))
                                )
                                run_new_test.click()
                                time.sleep(3)
                            except:
                                # Если кнопка не найдена, обновляем страницу
                                print(f"{Fore.YELLOW}Обновление страницы...{Style.RESET_ALL}")
                                driver.refresh()
                                time.sleep(5)
                                continue
                        
                        print(f"\n{Fore.CYAN}Проверка группы {group_index} из {total_groups}{Style.RESET_ALL}")
                        
                        # Проверяем наличие текстового поля несколько раз
                        textarea = None
                        for _ in range(3):
                            try:
                                textarea = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
                                )
                                if textarea.is_displayed():
                                    break
                            except:
                                driver.refresh()
                                time.sleep(3)
                        
                        if not textarea or not textarea.is_displayed():
                            raise Exception("Не удалось найти текстовое поле")
                        
                        proxy_list = []
                        for proxy in proxy_group:
                            proxy_str = f"{proxy['ip']}:{proxy['port']}:{proxy['login']}:{proxy['password']}"
                            proxy_list.append(proxy_str)
                        
                        textarea.clear()
                        textarea.send_keys('\n'.join(proxy_list))
                        
                        # Нажимаем кнопку проверки
                        check_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-1ot4que'))
                        )
                        check_button.click()
                        
                        # Увеличиваем время ожидания результатов
                        WebDriverWait(driver, 45).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.css-1vwd0hh'))
                        )
                        time.sleep(5)
                        
                        # Ждем завершения всех проверок
                        try:
                            # Ждем пока исчезнет индикатор загрузки или пройдет таймаут
                            WebDriverWait(driver, 60).until_not(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.css-loading-indicator'))
                            )
                        except:
                            pass  # Игнорируем ошибку таймаута
                        
                        # Собираем результаты текущей группы
                        success_count = 0
                        rows = driver.find_elements(By.CSS_SELECTOR, '.css-10hyo0x .css-zuuxtj')
                        
                        if not rows:
                            print(f"{Fore.YELLOW}Предупреждение: Нет результатов для текущей группы{Style.RESET_ALL}")
                            # Проверяем наличие ошибок на странице
                            try:
                                error_elements = driver.find_elements(By.CSS_SELECTOR, '.css-error-message')
                                if error_elements:
                                    for error in error_elements:
                                        print(f"{Fore.RED}Ошибка прокси: {error.text}{Style.RESET_ALL}")
                            except:
                                pass
                            continue
                            
                        for row in rows:
                            try:
                                cells = row.find_elements(By.CSS_SELECTOR, '.css-1rucjik')
                                if len(cells) >= 5:
                                    result = {
                                        'proxy': cells[0].find_element(By.CSS_SELECTOR, '.css-19z6wwy').text,
                                        'status': cells[1].text,
                                        'ip': cells[2].text,
                                        'quality': cells[3].text.replace('high', 'High').replace('low', 'Low'),
                                        'risk': cells[4].text
                                    }
                                    
                                    if result['status'] == 'Success':
                                        success_count += 1
                                        all_results.append(result)
                                        
                                        # Определяем качество и сохраняем прокси
                                        quality = result['quality'].lower()
                                        if quality == 'high':
                                            quality_proxies['high'].append(result['proxy'])
                                        elif quality == 'medium':
                                            quality_proxies['medium'].append(result['proxy'])
                                        else:
                                            quality_proxies['low'].append(result['proxy'])
                                        
                                        # Вывод в консоль
                                        status_color = Fore.GREEN
                                        quality_color = Fore.GREEN if 'High' in result['quality'] else Fore.RED
                                        
                                        print(f"{Fore.WHITE}Прокси:{Style.RESET_ALL} {result['proxy']}")
                                        print(f"{Fore.WHITE}Статус:{Style.RESET_ALL} {status_color}{result['status']}{Style.RESET_ALL}")
                                        print(f"{Fore.WHITE}IP:{Style.RESET_ALL} {result['ip']}")
                                        print(f"{Fore.WHITE}Качество:{Style.RESET_ALL} {quality_color}{result['quality']}{Style.RESET_ALL}")
                                        print(f"{Fore.WHITE}Риск:{Style.RESET_ALL} {result['risk']}")
                                        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")
                                    else:
                                        # Сохраняем нерабочие прокси
                                        quality_proxies['not_working'].append(result['proxy'])
                                    
                            except Exception as e:
                                print(f"{Fore.YELLOW}Ошибка при обработке результата: {e}{Style.RESET_ALL}")
                                continue
                        
                        print(f"\n{Fore.CYAN}В группе {group_index} успешно проверено: {success_count} из {len(proxy_group)} прокси{Style.RESET_ALL}")
                        
                        # Сохраняем промежуточные результаты после каждой группы
                        for quality, proxies_list in quality_proxies.items():
                            if proxies_list:
                                with open(f'results/{quality}.txt', 'w', encoding='utf-8') as f:
                                    f.write('\n'.join(proxies_list))
                        
                        print(f"\n{Fore.CYAN}Прогресс: {group_index}/{total_groups} групп проверено{Style.RESET_ALL}")
                        
                        success = True  # Если дошли до этого места, значит всё успешно
                        
                    except Exception as e:
                        retry_count += 1
                        print(f"{Fore.RED}Ошибка при проверке группы {group_index}: {e}{Style.RESET_ALL}")
                        
                        if retry_count >= MAX_RETRIES:
                            print(f"{Fore.RED}Исчерпаны все попытки для группы {group_index}{Style.RESET_ALL}")
                            # Сохраняем промежуточные результаты
                            for quality, proxies_list in quality_proxies.items():
                                if proxies_list:
                                    with open(f'results/{quality}.txt', 'w', encoding='utf-8') as f:
                                        f.write('\n'.join(proxies_list))
                        else:
                            print(f"{Fore.YELLOW}Подготовка к повторной попытке...{Style.RESET_ALL}")
                            time.sleep(5)  # Пауза перед следующей попыткой
                            
            # Выводим итоговую статистику
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"Проверка завершена. Итоговые результаты:")
            for quality, proxies_list in quality_proxies.items():
                if quality == 'not_working':
                    print(f"{Fore.RED}Нерабочие: {len(proxies_list)} прокси{Style.RESET_ALL}")
                else:
                    print(f"{quality.capitalize()}: {len(proxies_list)} прокси")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            
            return all_results  # Возвращаем все результаты
            
        except Exception as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            raise e
            
        finally:
            if driver:
                driver.quit() 

    def _get_extension_uuid(self, driver):
        extension_info = driver.find_elements(By.CSS_SELECTOR, ".qa-debug-target-item")
        for item in extension_info:
            try:
                name = item.find_element(By.CSS_SELECTOR, ".debug-target-item__name").text
                if "Bulk Proxy Checker" in name:
                    manifest_link = item.find_element(By.CSS_SELECTOR, ".qa-manifest-url")
                    manifest_url = manifest_link.get_attribute("href")
                    return manifest_url.split("moz-extension://")[1].split("/")[0]
            except:
                continue
        raise Exception("Не удалось найти UUID расширения")

    def _open_extension_popup(self, driver, extension_uuid):
        popup_paths = ["/popup.html", "/popup/popup.html", "/html/popup.html", "/index.html", "/popup/index.html"]
        for path in popup_paths:
            try:
                popup_url = f"moz-extension://{extension_uuid}{path}"
                driver.get(popup_url)
                time.sleep(1)
                if "Файл не найден" not in driver.title:
                    return True
            except:
                continue
        raise Exception("Не удалось найти правильный путь к popup окну расширения") 