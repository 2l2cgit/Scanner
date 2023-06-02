import socket
import requests
import threading
from colorama import Fore, init
import sys

init()

logo = '''
  _   _ _____ _______ _____  _____          _   _ 
 | \ | |  __ \__   __/ ____|/ ____|   /\   | \ | |
 |  \| | |__) | | | | (___ | |       /  \  |  \| |
 | . ` |  ___/  | |  \___ \| |      / /\ \ | . ` |
 | |\  | |      | |  ____) | |____ / ____ \| |\  |
 |_| \_|_|      |_| |_____/ \_____/_/    \_\_| \_|

  
'''

print(f"{Fore.RED}{logo}{Fore.RESET}")

def ping_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set the timeout for connection attempts
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except socket.timeout:
        return False

def check_port(ip, port):
    try:
        response = requests.get(f'https://api.mcsrvstat.us/2/{ip}:{port}')
        data = response.json()

        if response.status_code == 200 and data['online']:
            player_count = data['players']['online']
            max_players = data['players']['max']
            motd = data['motd']['clean'][0]

            player_info = f"{player_count}/{max_players}"

            print(f"{Fore.RED}({ip}:{port}){Fore.BLUE}({player_count}/{Fore.LIGHTYELLOW_EX}{max_players}){Fore.RESET} ({motd}){Fore.RESET}")
        else:
            print(f"{Fore.RED}({ip}:{port}){Fore.RESET} (Invalid MOTD){Fore.RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}({ip}:{port}){Fore.RESET} Failed to get server info... Error: {str(e)}")

def scan_ports(ip, start_port, end_port):
    responsive_ports = []
    for port in range(start_port, end_port + 1):
        if ping_port(ip, port):
            responsive_ports.append(port)

    for port in responsive_ports:
        check_port(ip, port)

# Example usage
server_ip = input("Insert the IP: ")

print('═════════════════════════')
print(f'{Fore.RESET} Scanning {Fore.GREEN}{server_ip}{Fore.RESET}')
print('═════════════════════════')

response = requests.get(f'https://api.mcsrvstat.us/2/{server_ip}')
data = response.json()

if response.status_code == 200:
    ip_address = data.get("ip")

    if ip_address:
        start_port = 25500
        end_port = 25600

        # Define the number of threads to use
        num_threads = 10

        # Calculate the number of ports to scan per thread
        ports_per_thread = (end_port - start_port + 1) // num_threads

        # Create and start the threads
        threads = []
        for i in range(num_threads):
            thread_start_port = start_port + (i * ports_per_thread)
            thread_end_port = thread_start_port + ports_per_thread - 1

            thread = threading.Thread(target=scan_ports, args=(ip_address, thread_start_port, thread_end_port))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()
    else:
        print("Failed to retrieve server IP from the API.")
else:
    print("Failed to retrieve server information from the API.")