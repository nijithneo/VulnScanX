import os
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from colorama import Fore, Style  # Import colorama library

def read_payloads_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            payloads = f.readlines()
        return [payload.strip() for payload in payloads]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

def display_banner():
    banner = f"""
{Fore.RED}                      .^?5GB#######BG57^          
                     J#BP?!~~~~~~~~~!JPBB5~       
                  ?? :^:!JPGBBGGGBBGPJ~:~Y&#?.    
                :.!! ~P#BY!^..   ..^75B#5^.?&#!   
               5@! ^G@5^               ~P@P:.P@J  
              P@J 7@B^                   ~#&~ Y@Y 
             ?@5 !@G.    :!?YPPPPPY7~:    :#@^ G@!
             #@: #@:  :JB#&@&Y!~75@@##G?.  ~@G ~@B
            :@# ^@G  J@#!.B@^ ^Y: ~@G.7#@?  #&..&@
            :@# ^@B  7##J~B@! :7. 7@G~Y&B! .#&..&@
             B@^ B@~   !5B#@@GJ?YB@@#B5~   !@P !@G
             !@G ^@#:     :~7JJYJ?7~:     ^@&: B@~
              J@5 ^#&!                    ^J: G@7 
               ?@G:.Y&B7.               YP  ^#@7  
            ^~^7&&&Y::?B#GJ!^::::^~7YGY  .^P@P^   
          7B#G#@G:Y@@P7^^!JPGGGGGGG5J!^^?G&P~     
       .?#&J: :J##&5~?G#B5J7!~~~~~!7JPB#P?:       
     .?##J.     ^&@:   .^7J5PGGGGGP5J7^.          
   .J&#?.     .J##7                               
 :Y&#7.     :J&#?.                                
J&B7      :Y&B7                                   
&@7     :5&B!                                     
:Y&B7.^5&G!                                       
  :5&#&G!                                         
{Style.RESET_ALL}
{'Security Testing Tool for XSS, SQLi, and RCE'}
{'Author: github.com/neoxxz'}
"""

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
                        print(f"Payload: {payload} - SQL Injection FOUND! (Method 3) - Status code: {response.status_code}")
                    else:
                        print(f"Payload: {payload} - Not Vulnerable (Method 3) - Status code: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"Error (requests): {e}")

        else:
            print("Invalid SQL injection method. Please enter either '1', '2', or '3'.")

    except Exception as e:
        print(f"Error: {e}")


def test_remote_code_execution(url, payloads):
    try:
        for payload in payloads:
            payload = payload.strip()  # Remove leading/trailing whitespaces and newlines
            try:
                headers = {'User-Agent': payload}
                response = requests.get(url, headers=headers)

                if 'RCE_SUCCESS' in response.text:
                    print(f"Payload: {payload} - Remote Code Execution FOUND!")
                else:
                    print(f"Payload: {payload} - Not Vulnerable to Remote Code Execution")

            except requests.exceptions.RequestException as e:
                print(f"Error (requests): {e}")

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
            print("5. Quit")
            choice = input("Enter your choice (1, 2, 3, 4, or 5): ")

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
                test_remote_code_execution(url, rce_payloads)
            elif choice == '5':
                print("Exiting VulnScanX. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter a valid option (1, 2, 3, 4, or 5).")

    except FileNotFoundError:
        print("One or more payload files not found.")
    except KeyboardInterrupt:
        print("\nVulnScanX terminated by user. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
