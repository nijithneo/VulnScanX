# VulnScanX v1.1

VulnScanX v2.0 is a versatile and user-friendly command-line application designed to assist developers and security professionals in identifying vulnerabilities in web applications. The tool primarily focuses on testing for three critical security vulnerabilities: Cross-Site Scripting (XSS), SQL Injection (SQLi), and Remote Code Execution (RCE).

## Features

- **Reflected XSS Testing (via requests):** Test for reflected XSS vulnerabilities by injecting payloads into the URL parameters and observing the response for potential script execution.

- **DOM-based XSS Testing (via Selenium):** Perform DOM-based XSS testing using Selenium with support for multiple web browsers. VulnScanX v2.0 now supports Chrome and Firefox.

- **SQL Injection Testing (via requests):** Detect SQL Injection vulnerabilities by injecting malicious SQL code into the application's input fields and monitoring for SQL errors in the responses.

- **Remote Code Execution Testing (via requests):** Test for Remote Code Execution vulnerabilities by injecting OS commands and observing the application's response.

- **Server-Side Template Injection (via requests):** Identify potential Server-Side Template Injection vulnerabilities by injecting template-related payloads and analyzing the application's behavior.

- **Open Redirection Testing (via requests):** Assess the security of redirection URLs and detect potential vulnerabilities related to unvalidated redirects.

- **Multithreading Support:** VulnScanX v2.0 now supports multithreading, allowing concurrent testing of payloads. With this feature, users can test multiple payloads simultaneously, significantly reducing testing time and enhancing overall efficiency.

- **Automated Link Crawling and Testing:** The new `crawl_and_test_links` function enables VulnScanX to automatically crawl and test links within the target website up to a specified depth. This feature ensures thorough scanning of the entire website, leaving no potential vulnerabilities unexplored.

- **Logging of Results:** VulnScanX v2.0 logs all testing results to a file named `vulnscanx_results.log`. This logging feature provides users with a detailed record of the vulnerability scanning process, facilitating easy review, analysis, and tracking of identified issues.

- **Improved User Interface:** The main loop of VulnScanX has been revamped to provide an improved user interface. Users can now choose from a range of testing methods, including Reflected XSS, DOM-based XSS, SQL Injection, Remote Code Execution, Server-Side Template Injection, and Open Redirection. The program offers clear instructions and options for a more user-friendly experience.

- **Payload File Import Improvements:** The payload loading mechanism has been enhanced to handle payloads more efficiently. Users can easily import payloads from external files and customize the testing process as needed.

## Usage

1. Clone the repository: `git clone https://github.com/neoxxz/VulnScanX.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Customize payload files in the 'Payloads' folder for specific testing needs.
4. Run the tool: `python Main.py`
5. Follow the on-screen instructions to select the testing method and provide the target URL.

## Customize Payloads

- XSS payloads: Add or modify payloads in `Payloads/PayloadXSS.txt`.
- SQL Injection payloads: Add or modify payloads in `Payloads/PayloadSQL.txt`.
- Remote Code Execution payloads: Add or modify payloads in `Payloads/PayloadRCE.txt`.
- Server-Side Template Injection payloads: Add or modify payloads in `Payloads/PayloadSSTI.txt`.
- Open Redirection payloads: Add or modify payloads in `Payloads/PayloadOpenRed.txt`.

## Suggest Features

If you have any suggestions for additional features or improvements, feel free to open an issue or create a pull request on the repository. Your contributions are welcome!

## License

This project is licensed under the [MIT License](https://github.com/neoxxz/VulnScanX/blob/main/LICENSE).

## Disclaimer

This tool is intended for ethical use only. Always seek proper authorization before conducting security testing on web applications. The developers are not responsible for any unauthorized or illegal usage.
