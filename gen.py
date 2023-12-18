import tls_client
import uuid
import ctypes
from concurrent.futures import ThreadPoolExecutor
import threading
import requests
from colorama import Fore, Style, init
from datetime import datetime
import time
import os
from traceback import print_exc

lock = threading.Lock()
genned = 0
webhook_url = ""  # Global variable to store the webhook URL
file_name = "promos.txt"  # Default file name for saving promo codes
stats_file_name = "stats.txt"  # File name for saving statistics
ui_color = Fore.LIGHTMAGENTA_EX

class Logger:
    @staticmethod
    def print_banner():
        banner = r"""
 ▒█████  ██▒   █▓█████ ██▀███ ▓█████▄ █    ██  ██████▄▄▄█████▓ ██████    ▄▄▄█████▓▒█████  ▒█████  ██▓    
▒██▒  ██▓██░   █▓█   ▀▓██ ▒ ██▒██▀ ██▌██  ▓██▒██    ▒▓  ██▒ ▓▒██    ▒    ▓  ██▒ ▓▒██▒  ██▒██▒  ██▓██▒    
▒██░  ██▒▓██  █▒▒███  ▓██ ░▄█ ░██   █▓██  ▒██░ ▓██▄  ▒ ▓██░ ▒░ ▓██▄      ▒ ▓██░ ▒▒██░  ██▒██░  ██▒██░    
▒██   ██░ ▒██ █░▒▓█  ▄▒██▀▀█▄ ░▓█▄   ▓▓█  ░██░ ▒   ██░ ▓██▓ ░  ▒   ██▒   ░ ▓██▓ ░▒██   ██▒██   ██▒██░    
░ ████▓▒░  ▒▀█░ ░▒████░██▓ ▒██░▒████▓▒▒█████▓▒██████▒▒ ▒██▒ ░▒██████▒▒     ▒██▒ ░░ ████▓▒░ ████▓▒░██████▒
░ ▒░▒░▒░   ░ ▐░ ░░ ▒░ ░ ▒▓ ░▒▓░▒▒▓  ▒░▒▓▒ ▒ ▒▒ ▒▓▒ ▒ ░ ▒ ░░  ▒ ▒▓▒ ▒ ░     ▒ ░░  ░ ▒░▒░▒░░ ▒░▒░▒░░ ▒░▓  ░
  ░ ▒ ▒░   ░ ░░  ░ ░  ░ ░▒ ░ ▒░░ ▒  ▒░░▒░ ░ ░░ ░▒  ░ ░   ░   ░ ░▒  ░ ░       ░     ░ ▒ ▒░  ░ ▒ ▒░░ ░ ▒  ░
░ ░ ░ ▒      ░░    ░    ░░   ░ ░ ░  ░ ░░░ ░ ░░  ░  ░   ░     ░  ░  ░       ░     ░ ░ ░ ▒ ░ ░ ░ ▒   ░ ░   
    ░ ░       ░    ░  ░  ░       ░      ░          ░               ░                 ░ ░     ░ ░     ░  ░
             ░                 ░                                                                         
"""
        lines = banner.split('\n')
        max_width = max(len(line) for line in lines)
        center_offset = (os.get_terminal_size().columns - max_width) // 2

        print(ui_color + Style.BRIGHT)
        for line in lines:
            print(" " * center_offset + line)
        print(Fore.RESET + Style.RESET_ALL)

    # ... (rest of the Logger class remains unchanged)

    @staticmethod
    def print_menu():
        options = ["1. Customize UI Color", "2. Promo Code Generation", "3. Support", "4. Set Webhook", "5. Set File Name", "6. Exit"]
        max_width = max(len(option) for option in options)
        center_offset = (os.get_terminal_size().columns - max_width) // 2

        print(ui_color + Style.BRIGHT)
        for option in options:
            print(" " * center_offset + option)
        print(Fore.RESET + Style.RESET_ALL)

    @staticmethod
    def sprint(tag: str, content: str, color):
        ts = f"{Fore.RESET}{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{Fore.RESET}"
        with lock:
            print(Style.BRIGHT + ts + color + f" [{tag}] " + Fore.RESET + content + Fore.RESET)

    @staticmethod
    def ask(tag: str, content: str, color):
        ts = f"{Fore.RESET}{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{Fore.RESET}"
        return input(Style.BRIGHT + ts + color + f" [{tag}] " + Fore.RESET + content + Fore.RESET)

def update_title():
    ctypes.windll.kernel32.SetConsoleTitleW(f"Spirit Gen | Generated: {genned}")

class OperaGX:
    def __init__(self, proxy) -> None:
        self.session = tls_client.Session(client_identifier="chrome112")
        self.proxy = proxy
        self.start_time = time.time()
        self.generate_promo_code()

    def make_post_request(self, *args, **kwargs):
        while True:
            try:
                return self.session.post(*args, **kwargs)
            except Exception as e:
                continue

    def generate_promo_code(self):
        global genned
        response = self.make_post_request('https://api.discord.gx.games/v1/direct-fulfillment', json={
            'partnerUserId': str(uuid.uuid4()),
        }, proxy=self.proxy)

        elapsed_time = time.time() - self.start_time
        speed = genned / elapsed_time if elapsed_time > 0 else 0

        if response.status_code == 429:
            Logger.sprint("RATELIMIT", "You are being rate-limited!", Fore.LIGHTYELLOW_EX)
            return

        ptoken = response.json()['token']
        link = f"https://discord.com/billing/partner-promotions/1180231712274387115/{ptoken}"
        Logger.sprint(f"PROMO", link, Fore.LIGHTGREEN_EX)

        with lock:
            open(file_name, 'a').write(f"{link}\n")
            update_title()

            # Save stats to the stats file
            stats_content = f"Promo Code Stats:\nGenerated: {genned}\nTime Elapsed: {elapsed_time:.2f} seconds\nSpeed: {speed:.2f} codes/sec\n\n"
            open(stats_file_name, 'a').write(stats_content)

            # Send stats to the Discord webhook
            self.send_to_discord_webhook(link, speed)

        genned += 1

    def send_to_discord_webhook(self, promo_link, speed):
        global webhook_url
        if webhook_url:
            content = f"New Promo Code Generated:\n{promo_link}\nSpeed: {speed:.2f} codes/sec\nTotal Generated: {genned}"
            payload = {"content": content}
            retry_delay = 1  # Initial delay in seconds
            max_retries = 5  # Maximum number of retries

            for attempt in range(max_retries):
                try:
                    requests.post(webhook_url, json=payload)
                    Logger.sprint("WEBHOOK", "Promo code sent to Discord webhook", Fore.LIGHTMAGENTA_EX)
                    break  # Break out of the loop if successful
                except requests.exceptions.RequestException as e:
                    Logger.sprint("WEBHOOK", f"Error sending promo code to Discord webhook: {e}", Fore.LIGHTRED_EX)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff for the next attempt



def customize_ui_color():
    global genned, webhook_url, file_name, ui_color  # Reset global variables
    color_name = Logger.ask("COLOR", "Enter the name of the color you want for UI: ", Fore.LIGHTMAGENTA_EX)
    ui_color = getattr(Fore, color_name.upper(), Fore.LIGHTMAGENTA_EX)
    init(convert=True)
    Logger.sprint("UI", f"UI color set to {color_name}", ui_color)
    time.sleep(1)  # Pause for 1 second to display the message

def support_option():
    Logger.sprint("SUPPORT", "Discord - overdusts", Fore.LIGHTMAGENTA_EX)

def set_webhook():
    global webhook_url
    webhook_url = Logger.ask("WEBHOOK", "Enter your Discord webhook URL (leave empty to skip): ", Fore.LIGHTMAGENTA_EX).strip()

def set_file_name():
    global file_name
    file_name = Logger.ask("FILE NAME", "Enter the file name for saving promo codes: ", Fore.LIGHTMAGENTA_EX).strip()

def main_menu():
    while True:
        Logger.print_banner()
        Logger.print_menu()
        choice = Logger.ask("CHOICE", "Enter your choice: ", Fore.LIGHTBLUE_EX)

        if choice == '1':
            customize_ui_color()
        elif choice == '2':
            promo_gen_menu()
        elif choice == '3':
            support_option()
        elif choice == '4':
            set_webhook()
        elif choice == '5':
            set_file_name()
        elif choice == '6':
            Logger.sprint("EXIT", "Exiting Spirit Gen. Goodbye!", Fore.LIGHTWHITE_EX)
            break
        else:
            Logger.sprint("ERROR", "Invalid choice. Please enter a valid option.", Fore.LIGHTRED_EX)

        # Pause for 1 second before clearing the console
        time.sleep(1)
        # Clear the console after executing an option
        os.system('cls' if os.name == 'nt' else 'clear')

def promo_gen_menu():
    try:
        proxy = "http://" + choice(open("proxies.txt").read().splitlines())
    except Exception as e:
        print_exc()
        proxy = None

    t = int(Logger.ask("THREADS", "Enter the number of threads -> ", Fore.LIGHTBLUE_EX))

    with ThreadPoolExecutor(max_workers=t + 1) as executor:
        for _ in range(t):
            executor.submit(OperaGX, proxy)


if __name__ == "__main__":
    init()
    main_menu()
