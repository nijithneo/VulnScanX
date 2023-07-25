# VulnScanX

VulnScanX is a versatile and user-friendly command-line application designed to assist developers and security professionals in identifying vulnerabilities in web applications. The tool primarily focuses on testing for three critical security vulnerabilities: Cross-Site Scripting (XSS), SQL Injection (SQLi), and Remote Code Execution (RCE).

## Features

- Reflected XSS Testing (via requests)
- DOM-based XSS Testing (via Selenium)
- SQL Injection Testing (via requests)
- Remote Code Execution Testing (via requests)

## Usage

1. Clone the repository: `git clone https://github.com/neoxxz/VulnScanX.git`
2. Install the required dependencies: `pip install colorama`
3. Customize payload files in the 'Payloads' folder for specific testing needs.
4. Run the tool: `python Main.py`
5. Follow the on-screen instructions to select the testing method and provide the target URL.

## Customize Payloads

- XSS payloads: Add or modify payloads in 'Payloads/PayloadXSS.txt'.
- SQL Injection payloads: Add or modify payloads in 'Payloads/PayloadSQL.txt'.
- Remote Code Execution payloads: Add or modify payloads in 'Payloads/PayloadRCE.txt'.

## Disclaimer

This tool is intended for ethical use only. Always seek proper authorization before conducting security testing on web applications. The developers are not responsible for any unauthorized or illegal usage.
