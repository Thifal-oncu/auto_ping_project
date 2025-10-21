#!/usr/bin/env python3
from scapy.all import IP, ICMP, sr1, conf
import sys
import time

def traceroute(target, max_hops=30, timeout=2):
    print(f"Traceroute ke {target}, maksimum {max_hops} hop:\n")

    conf.verb = 0  # nonaktifkan output detail scapy

    for ttl in range(1, max_hops + 1):
        pkt = IP(dst=target, ttl=ttl) / ICMP()
        start_time = time.time()
        reply = sr1(pkt, verbose=0, timeout=timeout)
        end_time = time.time()
        rtt = round((end_time - start_time) * 1000, 2)

        if reply is None:
            print(f"{ttl:2d}  * * *  (timeout)")
        elif reply.type == 11:  # Time Exceeded
            print(f"{ttl:2d}  {reply.src:<15}  {rtt} ms")
        elif reply.type == 0:   # Echo Reply (tujuan tercapai)
            print(f"{ttl:2d}  {reply.src:<15}  {rtt} ms  (selesai)")
            break
        else:
            print(f"{ttl:2d}  {reply.src:<15}  (tipe ICMP {reply.type})")

    print("\nTraceroute selesai.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: sudo python3 traceroute.py <domain/IP>")
        sys.exit(1)

    target = sys.argv[1]
    traceroute(target)
