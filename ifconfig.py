#!/usr/bin/env python3
"""
disable_if_internet_down.py
- Cek koneksi internet (8.8.8.8:53)
- Jika down: disable interface default (Linux/Windows/macOS)
- Butuh run as root/Administrator
"""

import socket
import subprocess
import platform
import sys
import argparse
import shlex
import re

CHECK_HOST = ("8.8.8.8", 53)
TIMEOUT = 3.0

def internet_up(timeout=TIMEOUT):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(CHECK_HOST)
        sock.close()
        return True
    except Exception:
        return False

# --- Helpers per OS ---
def linux_get_default_iface():
    try:
        proc = subprocess.run(["ip", "route", "get", CHECK_HOST[0]], capture_output=True, text=True, check=False)
        out = proc.stdout.strip()
        # contoh output: "8.8.8.8 via 192.168.1.1 dev wlp3s0 src 192.168.1.100 uid 1000"
        m = re.search(r" dev (\S+)", out)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None

def linux_down_iface(iface, dry=False):
    if not iface:
        print("Tidak dapat menentukan interface default.")
        return False
    cmd = ["ip", "link", "set", "dev", iface, "down"]
    if dry:
        print("[DRY RUN] " + " ".join(shlex.quote(c) for c in cmd))
        return True
    print(f"Men-disable interface {iface} (Linux)...")
    p = subprocess.run(cmd, check=False)
    return p.returncode == 0

def macos_get_default_iface():
    # macOS: gunakan route get
    try:
        proc = subprocess.run(["route", "get", CHECK_HOST[0]], capture_output=True, text=True, check=False)
        out = proc.stdout
        m = re.search(r"interface: (\S+)", out)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None

def macos_down_iface(iface, dry=False):
    if not iface:
        print("Tidak dapat menentukan interface default.")
        return False
    cmd = ["ifconfig", iface, "down"]
    if dry:
        print("[DRY RUN] " + " ".join(shlex.quote(c) for c in cmd))
        return True
    print(f"Men-disable interface {iface} (macOS)...")
    p = subprocess.run(cmd, check=False)
    return p.returncode == 0

def windows_get_connected_interfaces():
    try:
        proc = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True, check=False)
        out = proc.stdout.splitlines()
        # Format: Admin State    State    Type     Interface Name
        # Kita cari baris dengan "Connected"
        iface_names = []
        for line in out:
            if "Connected" in line:
                # ambil kolom terakhir
                parts = line.strip().split()
                if len(parts) >= 4:
                    name = " ".join(parts[3:])
                    iface_names.append(name)
        return iface_names
    except Exception:
        return []

def windows_disable_interface(name, dry=False):
    cmd = ["netsh", "interface", "set", "interface", name, "disable"]
    if dry:
        print("[DRY RUN] " + " ".join(shlex.quote(c) for c in cmd))
        return True
    print(f"Men-disable interface '{name}' (Windows)...")
    p = subprocess.run(cmd, check=False, shell=True)  # netsh kadang butuh shell on some env
    return p.returncode == 0

# --- Main logic ---
def main(dry=False, force=False):
    print("Cek koneksi internet...")
    up = internet_up()
    print("Internet up?" , up)
    if up and not force:
        print("Internet tersedia. Tidak ada aksi dilakukan.")
        return

    osn = platform.system().lower()
    print("OS detected:", osn)

    if osn == "linux":
        iface = linux_get_default_iface()
        if not iface:
            print("Gagal menentukan interface default. Coba manual.")
        success = linux_down_iface(iface, dry=dry)
        print("Selesai." if success else "Gagal men-disable interface.")
    elif osn == "darwin":
        iface = macos_get_default_iface()
        success = macos_down_iface(iface, dry=dry)
        print("Selesai." if success else "Gagal men-disable interface.")
    elif osn == "windows":
        ifaces = windows_get_connected_interfaces()
        if not ifaces:
            print("Tidak menemukan interface Connected melalui netsh.")
            return
        ok_all = True
        for iface in ifaces:
            ok = windows_disable_interface(iface, dry=dry)
            ok_all = ok_all and ok
        print("Selesai." if ok_all else "Beberapa interface gagal di-disable.")
    else:
        print("OS tidak dikenali/sedang tidak didukung oleh skrip ini.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disable network interface when internet down.")
    parser.add_argument("--dry", action="store_true", help="Dry run: tampilkan perintah tanpa mengeksekusi")
    parser.add_argument("--force", action="store_true", help="Force disable meskipun koneksi terlihat up")
    args = parser.parse_args()
    try:
        main(dry=args.dry, force=args.force)
    except PermissionError:
        print("Script harus dijalankan dengan hak Administrator/root.")
    except Exception as e:
        print("Terjadi error:", e)
        sys.exit(2)