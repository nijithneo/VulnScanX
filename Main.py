import sys
import os
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from colorama import Fore, Style  # Import colorama library
from Config.Update import check_for_updates

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
        print(banner)

def test_reflected_xss_payloads(url, payloads):
    try:
        for payload in payloads:
            payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
            try:
                data = {'message': payload}
                response = requests.post(url, data=data)

                if 'XSS' in response.text:
                    print(f"Payload: {payload} - Reflected XSS FOUND! (via requests)")
                else:
                    print(f"Payload: {payload} - Status code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Error (requests): {e}")

    except Exception as e:
        print(f"Error: {e}")

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
                    # Execute the payload using JavaScript in the context of the page
                    driver.execute_script(f"document.getElementById('message').value = '{payload}';")
                    driver.execute_script("document.getElementById('submit').click();")

                    # Wait for some time to let the page respond (you can adjust the time if needed)
                    driver.implicitly_wait(5)

                    try:
                        # Check if the payload executed successfully
                        if 'XSS' in driver.page_source:
                            print(f"Payload: {payload} - DOM-based XSS FOUND! (via {browser})")
                        else:
                            print(f"Payload: {payload} - No XSS (via {browser})")
                    except NoSuchElementException:
                        # If the element with ID 'message' or 'submit' is not found, continue to the next payload
                        print(f"Payload: {payload} - Element not found (via {browser})")

                except WebDriverException as e:
                    print(f"Error ({browser}): {e}")

        else:
            print("Unsupported browser. Please select a supported browser.")

    except Exception as e:
        print(f"Error: {e}")

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

                    if 'Login failed' not in response.text:
                        print(f"Payload: {payload} - SQL Injection FOUND! (Method 1) - Status code: {response.status_code}")
                    else:
                        print(f"Payload: {payload} - Not Vulnerable (Method 1) - Status code: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"Error (requests): {e}")

        elif method == '2':
            # Method 2: Injecting into POST form data
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    data = {'username': payload, 'password': 'dummy'}  # Adjust data fields as per the form
                    response = requests.post(url, data=data)

                    if 'Login failed' not in response.text:
                        print(f"Payload: {payload} - SQL Injection FOUND! (Method 2) - Status code: {response.status_code}")
                    else:
                        print(f"Payload: {payload} - Not Vulnerable (Method 2) - Status code: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"Error (requests): {e}")

        elif method == '3':
            # Method 3: Injecting into cookies
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    cookies = {'username': payload, 'password': payload}  # Adjust cookie names as per the website
                    response = requests.get(url, cookies=cookies)

                    if 'Login failed' not in response.text:
                        print(f"Payload: {payload} - SQL Injection (Method 3) - Status code: {response.status_code}")
                    else:
                        print(f"Payload: {payload} - Not Vulnerable (Method 3) - Status code: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"Error (requests): {e}")

        else:
            print("Invalid SQL injection method. Please enter either '1', '2', or '3'.")

    except Exception as e:
        print(f"Error: {e}")


def test_remote_code_execution(url, payloads, method):
    try:
        if method == '1':
            # Method 1: Injecting into URL parameters
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    response = requests.get(f"{url}?cmd={payload}")

                    if 'RCE_SUCCESS' in response.text:
                        print(f"Payload: {payload} - Remote Code Execution FOUND! (Method 1) - Status code: {response.status_code}")
                    else:
                        print(f"Payload: {payload} - Not Vulnerable (Method 1)")

                except requests.exceptions.RequestException as e:
                    print(f"Error (requests): {e}")

        elif method == '2':
            # Method 2: Injecting into POST form data
            for payload in payloads:
                payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
                try:
                    data = {'cmd': payload}  # Adjust data fields as per the form
                    response = requests.post(url, data=data)

                    if 'RCE_SUCCESS' in response.text:
                        print(f"Payload: {payload} - Remote Code Execution FOUND! (Method 2) - Status code: {response.status_code}")
                    else:
                        print(f"Payload: {payload} - Not Vulnerable (Method 2) - Status code: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"Error (requests): {e}")

        else:
            print("Invalid RCE method. Please enter either '1' or '2'.")

    except Exception as e:
        print(f"Error: {e}")

def main():
    try:
        with open('Payloads/PayloadXSS.txt', 'r', encoding='utf-8') as f:
            xss_payloads = f.readlines()

        with open('Payloads/PayloadSQL.txt', 'r', encoding='utf-8') as f:
            sql_payloads = f.readlines()

        with open('Payloads/PayloadRCE.txt', 'r', encoding='utf-8') as f:
            rce_payloads = f.readlines()

        display_banner()

        while True:
            print("Choose testing method:")
            print("1. Reflected XSS (via requests)")
            print("2. DOM-based XSS (via Selenium)")
            print("3. SQL Injection (via requests)")
            print("4. Remote Code Execution (via requests)")
            print("5. Check for Updates")
            print("6. Quit")
            choice = input("Enter your choice (1, 2, 3, 4, 5, or 6): ")

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
                print("Checking for updates...")
                if check_for_updates():
                    print("Exiting VulnScanX. Please restart to use the updated version.")
                    sys.exit(0)
            elif choice == '6':
                print("Exiting VulnScanX. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter a valid option (1, 2, 3, 4, 5, or 6).")

    except FileNotFoundError:
        print("One or more payload files not found.")
    except KeyboardInterrupt:
        print("\nVulnScanX terminated by the user. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
