import os
import requests
import logging
import sys
import threading
import hashlib
import shutil
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from colorama import Fore, Style
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Set up logging
logging.basicConfig(filename='vulnscanx_results.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def read_payloads_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            payloads = f.readlines()
        return [payload.strip() for payload in payloads]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

def read_banner():
    try:
        with open('Config/Banner.txt', 'r', encoding='utf-8') as f:
            banner = f.read()
            return banner
    except FileNotFoundError:
        print("Banner file (Config/Banner.txt) not found.")
        return ""

def display_banner():
    banner = read_banner()
    if banner:
        print(Fore.RED + banner + Style.RESET_ALL)

def print_success(message):
    print(Fore.GREEN + message + Style.RESET_ALL)

def print_warning(message):
    print(Fore.YELLOW + message + Style.RESET_ALL)

def print_error(message):
    print(Fore.RED + message + Style.RESET_ALL)

def test_reflected_xss_payloads(url, payloads):
    try:
        num_threads = 5  # Number of threads to run concurrently (you can adjust this as needed)
        payloads_per_thread = len(payloads) // num_threads

        def test_payloads_thread(payloads, thread_id):
            try:
                start_idx = thread_id * payloads_per_thread
                end_idx = start_idx + payloads_per_thread if thread_id < num_threads - 1 else len(payloads)

                for i in range(start_idx, end_idx):
                    payload = payloads[i].strip()
                    try:
                        data = {'message': payload}
                        response = requests.post(url, data=data)

                        if 'XSS' in response.text:
                            print_success(f"URL: {url} - Payload: {payload} - XSS Found(via requests)")
                        else:
                            print_warning(f"URL: {url} - Payload: {payload} - No XSS (via requests)")

                    except requests.exceptions.RequestException as e:
                        print_error(f"Error (requests): {e}")

            except Exception as e:
                print_error(f"Error in test_payloads_thread: {e}")

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=test_payloads_thread, args=(payloads, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        print_error(f"Error in test_reflected_xss_payloads: {e}")

def test_dom_based_xss_payloads(url, payloads, browser):
    try:
        driver = None
        if browser.lower() == 'chrome':
            driver = webdriver.Chrome()
        elif browser.lower() == 'firefox':
            driver = webdriver.Firefox()
        # Add other supported browsers here

        if driver:
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    driver.get(url)
                    wait = WebDriverWait(driver, 10)  # Set a timeout of 10 seconds

                    # Try locating the element using different methods
                    element_methods = [
                        ("ID", By.ID),
                        ("Name", By.NAME),
                        ("Class Name", By.CLASS_NAME),
                        ("XPath", By.XPATH)
                    ]

                    element_found = False
                    for method_name, method in element_methods:
                        try:
                            element = wait.until(EC.presence_of_element_located((method, 'message')))
                            element_found = True
                            break
                        except NoSuchElementException:
                            continue

                    if not element_found:
                        print_warning(f"Payload: {payload} - Element not found (via {browser})")
                        continue

                    submit_button = driver.find_element(By.NAME, 'submitbutton')
                    driver.execute_script("arguments[0].value = arguments[1]", element, payload)
                    driver.execute_script("arguments[0].click()", submit_button)

                    driver.implicitly_wait(5)

                    try:
                        if 'XSS' in driver.page_source:
                            print_success(f"Payload: {payload} - DOM-based XSS FOUND! (via {browser})")
                        else:
                            print_warning(f"Payload: {payload} - No XSS (via {browser})")
                    except NoSuchElementException:
                        print_warning(f"Payload: {payload} - Element not found (via {browser})")

                    # Print the page source to analyze the page structure
                    print(driver.page_source)

                except WebDriverException as e:
                    print_error(f"Error ({browser}): {e}")
                    break  # Exit the loop if any error occurs

        else:
            print_error("Unsupported browser. Please select a supported browser.")

    except Exception as e:
        print_error(f"Error: {e}")

    finally:
        if driver:
            driver.quit()

def test_sql_injection_payloads(url, payloads, method):
    try:
        if method == '1':
            # Method 1: Injecting into URL parameters
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    response = requests.get(f"{url}?username={payload}&password=dummy")

                    # Check for indicators of successful SQL injection
                    if response.status_code == 200 and 'Welcome' in response.text:
                        print_success(f"URL: {url} - Payload: {payload} - SQL Injection (Method 1) - Vulnerable")
                    else:
                        print_warning(f"URL: {url} - Payload: {payload} - Not Vulnerable (Method 1)")

                except requests.exceptions.RequestException as e:
                    print_error(f"Error (requests): {e}")

        elif method == '2':
            # Method 2: Injecting into POST form data
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    data = {'username': payload, 'password': 'dummy'}  # Adjust data fields as per the form
                    response = requests.post(url, data=data)

                    # Check for indicators of successful SQL injection
                    if response.status_code == 200 and 'Welcome' in response.text:
                        print_success(f"URL: {url} - Payload: {payload} - SQL Injection (Method 2) - Vulnerable")
                    else:
                        print_warning(f"URL: {url} - Payload: {payload} - Not Vulnerable (Method 2)")

                except requests.exceptions.RequestException as e:
                    print_error(f"Error (requests): {e}")

        elif method == '3':
            # Method 3: Injecting into cookies
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    cookies = {'username': payload, 'password': 'dummy'}  # Adjust cookie names as per the website
                    response = requests.get(url, cookies=cookies)

                    # Check for indicators of successful SQL injection
                    if response.status_code == 200 and 'Welcome' in response.text:
                        print_success(f"URL: {url} - Payload: {payload} - SQL Injection (Method 3) - Vulnerable")
                    else:
                        print_warning(f"URL: {url} - Payload: {payload} - Not Vulnerable (Method 3)")

                except requests.exceptions.RequestException as e:
                    print_error(f"Error (requests): {e}")

        else:
            print_error("Invalid SQL injection method. Please enter either '1', '2', or '3'.")

    except Exception as e:
        print_error(f"Error: {e}")

def test_remote_code_execution(url, payloads, method):
    try:
        if method == '1':
            # Method 1: Injecting into URL parameters
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    response = requests.get(f"{url}?cmd={payload}")

                    if 'RCE_SUCCESS' in response.text:
                        print_success(f"Payload: {payload} - Remote Code Execution FOUND! (Method 1)")
                    else:
                        print_warning(f"Payload: {payload} - Not Vulnerable (Method 1)")

                except requests.exceptions.RequestException as e:
                    print_error(f"Error (requests): {e}")

        elif method == '2':
            # Method 2: Injecting into POST form data
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    data = {'cmd': payload}  # Adjust data fields as per the form
                    response = requests.post(url, data=data)

                    if 'RCE_SUCCESS' in response.text:
                        print_success(f"Payload: {payload} - Remote Code Execution FOUND! (Method 2)")
                    else:
                        print_warning(f"Payload: {payload} - Not Vulnerable (Method 2)")

                except requests.exceptions.RequestException as e:
                    print_error(f"Error (requests): {e}")

        else:
            print_error("Invalid RCE method. Please enter either '1' or '2'.")

    except Exception as e:
        print_error(f"Error: {e}")

def test_server_side_template_injection(url, payloads):
    try:
        for payload in payloads:
            payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
            try:
                data = {'template': payload}  # Adjust the data field name as per the target application
                response = requests.post(url, data=data)

                if 'SSTI_SUCCESS' in response.text:
                    print_success(f"Payload: {payload} - Server-Side Template Injection FOUND!")
                else:
                    print_warning(f"Payload: {payload} - Not Vulnerable")

            except requests.exceptions.RequestException as e:
                print_error(f"Error (requests): {e}")

    except Exception as e:
        print_error(f"Error: {e}")

def test_open_redirection_payloads(url, payloads):
    try:
        for payload in payloads:
            payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
            try:
                response = requests.get(f"{url}?redirect={payload}", allow_redirects=False)

                if response.status_code == 302 and 'Location' in response.headers:
                    print_success(f"Payload: {payload} - Open Redirection FOUND!")
                    print_warning(f"Redirect URL: {response.headers['Location']}")
                else:
                    print_warning(f"Payload: {payload} - Not Vulnerable")

            except requests.exceptions.RequestException as e:
                print_error(f"Error (requests): {e}")

    except Exception as e:
        print_error(f"Error: {e}")

def get_links_from_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
            return links
        else:
            print_error(f"Failed to get links from page {url}. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print_error(f"Error (requests) while getting links from page {url}: {e}")
        return []
    
def crawl_and_test_links(base_url, xss_payloads, sql_payloads, rce_payloads, ssti_payloads, open_redirection_payloads, max_depth=3):
    visited_urls = set()

    def crawl(url, depth):
        try:
            if depth > max_depth or url in visited_urls:
                return

            visited_urls.add(url)
            print(f"Crawling: {url}")
            links = get_links_from_page(url)

            for link in links:
                test_reflected_xss_payloads(link, xss_payloads)
                test_dom_based_xss_payloads(link, xss_payloads, browser='chrome')
                test_sql_injection_payloads(link, sql_payloads, method='1')
                test_remote_code_execution(link, rce_payloads, method='1')
                test_open_redirection_payloads(link, open_redirection_payloads)
                test_server_side_template_injection(link, ssti_payloads)

                crawl(link, depth + 1)

        except Exception as e:
            print_error(f"Error in crawl function: {e}")

    crawl(base_url, 1)

def main():
    try:
        # Load XSS payloads from the file
        with open('Payloads/PayloadXSS.txt', 'r', encoding='utf-8') as f:
            xss_payloads = f.readlines()

        # Load SQL injection payloads from the file
        with open('Payloads/PayloadSQL.txt', 'r', encoding='utf-8') as f:
            sql_payloads = f.readlines()

        # Load Remote Code Execution payloads from the file
        with open('Payloads/PayloadRCE.txt', 'r', encoding='utf-8') as f:
            rce_payloads = f.readlines()

        # Load SSTI payloads from the file
        with open('Payloads/PayloadSSTI.txt', 'r', encoding='utf-8') as f:
            ssti_payloads = f.readlines()

        # Load Open Redirection payloads from the file
        with open('Payloads/PayloadOpenRed.txt', 'r', encoding='utf-8') as f:
            open_redirection_payloads = f.readlines()

        display_banner()

        while True:
            print("Choose testing method:")
            print("1. Reflected XSS (via requests)")
            print("2. DOM-based XSS (via Selenium)")
            print("3. SQL Injection (via requests)")
            print("4. Remote Code Execution (via requests)")
            print("5. Server-Side Template Injection (via requests)")
            print("6. Open Redirection (via requests)")
            print("7. Crawl and Test All")
            print("8. Quit")
            choice = input("Enter your choice (1, 2, 3, 4, 5, 6, 7, or 8): ")

            if choice == '1':
                url = input("Enter the URL where Reflected XSS payload will be submitted: ")
                test_reflected_xss_payloads(url, xss_payloads)
            elif choice == '2':
                url = input("Enter the URL where DOM-based XSS payload will be submitted: ")
                browser = input("Enter the browser you want to use (chrome / firefox): ")
                test_dom_based_xss_payloads(url, xss_payloads, browser)
            elif choice == '3':
                url = input("Enter the URL where SQL Injection payload will be submitted: ")
                print("Choose SQL injection method:")
                print("1. Injecting into URL parameters")
                print("2. Injecting into POST form data")
                print("3. Injecting into cookies")
                method = input("Enter your choice (1, 2, or 3): ")
                test_sql_injection_payloads(url, sql_payloads, method)
            elif choice == '4':
                url = input("Enter the URL where Remote Code Execution payload will be submitted: ")
                print("Choose RCE method:")
                print("1. Injecting into URL parameters")
                print("2. Injecting into POST form data")
                method = input("Enter your choice (1 or 2): ")
                test_remote_code_execution(url, rce_payloads, method)
            elif choice == '5':
                url = input("Enter the URL where SSTI payload will be submitted: ")
                test_server_side_template_injection(url, ssti_payloads)
            elif choice == '6':
                url = input("Enter the URL where Open Redirection payload will be tested: ")
                test_open_redirection_payloads(url, open_redirection_payloads)
            elif choice == '7':
                url = input("Enter the base URL to start crawling and testing: ")
                crawl_and_test_links(url, xss_payloads, sql_payloads, rce_payloads, ssti_payloads, open_redirection_payloads)
            elif choice == '8':
                print("Exiting VulnScanX. Goodbye!")
                sys.exit(0)
            else:
                print_error("Invalid choice. Please enter a valid option (1, 2, 3, 4, 5, 6, 7, or 8).")

    except FileNotFoundError:
        print_error("One or more payload files not found.")
    except KeyboardInterrupt:
        print("\nVulnScanX terminated by user. Goodbye!")
    except Exception as e:
        print_error(f"Error: {e}")

if __name__ == "__main__":
    main()
