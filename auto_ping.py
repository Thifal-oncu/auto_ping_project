#!/usr/bin/env python3
import os
import time
from datetime import datetime

# Daftar host atau IP yang akan diping
hosts = [
    "8.8.8.8",        # Google DNS
    "1.1.1.1",        # Cloudflare DNS
    "www.cisco.com",  # Situs Cisco
    "www.google.com"  # Situs Google
]

def ping_host(host):
    # Jalankan perintah ping sekali (-c 1 untuk Linux)
    response = os.system(f"ping -c 1 {host} > /dev/null 2>&1")
    return response == 0

def main():
    print("=== Automatic Ping Monitor ===\n")
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            for host in hosts:
                if ping_host(host):
                    print(f"{host:25} ✅  UP")
                else:
                    print(f"{host:25} ❌  DOWN")
            print("-" * 50)
            time.sleep(5)  # jeda 5 detik sebelum ping ulang
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")

if __name__ == "__main__":
    main()
