from scapy.all import *
import ipaddress
import nmap
import asyncio
import platform
import requests
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


SUBNETS = ["10.17.70.0/24", "10.17.71.0/24"]

@dataclass
class NeighborEntry:
    address: str = ""
    mac: str = ""
    response_time: str = ""
    hostname: str = ""



async def main():
    master_list = []

    while True:
        master_list.extend(arp_scan())

        master_list = ping_sweep(master_list)

        print(master_list)

        master_list = mDNS(master_list)

        master_list = enrichment(master_list)
            
        await asyncio.sleep(500)



def arp_scan():
    entries =[]

    for address in SUBNETS:
        ans, unans = srp(
            Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=address), 
            timeout=2,
            verbose=False)

        for sent, received in ans:
            ip = received.psrc      # sender IP address
            mac = received.hwsrc    # sender MAC address

            rtt = (received.time - sent.sent_time) * 1000   # sender response time
            rtt_ms = f"{rtt:.2f} ms"    # formatting rtt as a string and adding " ms" at the end

            entries.append(NeighborEntry(address=ip, mac=mac, response_time=rtt_ms))
    
    return entries



def ping_sweep(entries):

    try:
        result = subprocess.run(
            ["fping", "-g", "-a", "10.17.70.0/24"],
            capture_output=True,
            text=True,
            timeout=30
        )

        alive_hosts = result.stdout.splitlines()
        print(alive_hosts)

        existing_ips = {entry.address for entry in entries}

        for host in alive_hosts:
            if host not in existing_ips:
                entries.append(NeighborEntry(address=host))
        return entries

    except subprocess.TimeoutExpired:
        print("Ping timed out")
        return entries



def mDNS(entries):
    pass

def NetBIOS(entries):
    pass

# Adding OS name and possibly hostname info to existing instances of NeighborEntry
# Functionality seems slow and not getting data back from many hosts
def enrichment():
    nm = nmap.PortScanner()

    os_scan = nm.scan(hosts="10.17.70.0/24", arguments='-O -F')
    nm.scan(hosts="10.17.70.0/24", arguments='-sn')

    for host in nm.all_hosts():
        hostname = nm[host].hostname()
        print(f"The hostname for {host} is: {hostname}")

            # Check if any OS matches were found
        if 'osmatch' in nm[host] and len(nm[host]['osmatch']) > 0:
            # Grab the highest accuracy OS prediction
            best_match = nm[host]['osmatch'][0]
            os_name = best_match['name']
            accuracy = best_match['accuracy']
            
            print(f"OS Match: {os_name} (Accuracy: {accuracy}%)")
        else:
            print("OS Match: Could not reliably detect the OS.")



#get_ndp_table()
#print(arp_scan())
#ping_sweep()
#@asyncio.run(main())
enrichment()















#   MASTER_URL = url2="https://endoflife.date/api/all.json"

# linux_url="https://endoflife.date/api/linux.json"
# windows_url="https://endoflife.date/api/windows.json"
# macos_url="https://endoflife.date/api/macos.json"


async def outdated_os_check():
    while True:
        os_name="Darwin"

        linux_response = requests.get("https://endoflife.date/api/linux.json").json()
        windows_response = requests.get("https://endoflife.date/api/windows.json").json()
        macos_response = requests.get("https://endoflife.date/api/macos.json").json()

        found = False

        if os_name == "Linux":
            current_cycle = ".".join(platform.release().split(".")[:2])
            for release in linux_response:
                if current_cycle == release['cycle']:
                    found = True
                    eol = release['eol']

                    if eol and date.fromisoformat(eol) < date.today():
                        print("Kernel is outdated.")
                    else:
                        print("Kernel is supported.") # Kernel should be ahead of EoL
                    break

            if not found:
                print('Kernel not found in API') # Kernel may be either unsupported or new enough not to be found using the EoL api.






        test_tuple = ('11', '10.0.26200', 'SP0', 'Multiprocessor Free')


        if os_name == "Windows":
            current_cycle = ".".join(platform.release().split(".")[:1])
            for release in windows_response:
                print(test_tuple[1])
                print(f"{release['latest']}, {release['cycle']}\n")
                









        test_tuple2 = ('10.12', ('', '', ''), 'arm64')

        if os_name == "Darwin":

            if Decimal(test_tuple2[0]) < 11:
                current_cycle = ".".join(test_tuple2[0].split(".")[:2])
            
            if Decimal(test_tuple2[0]) >= 11:
                current_cycle = "".join(test_tuple2[0].split(".")[:1])

            for release in macos_response:

                if current_cycle == release['cycle']:

                    found = True

                    eol = release['eol']

                    if eol and date.fromisoformat(eol) < date.today():
                        print(f"{release['codename']} is outdated.")

                    else:
                        print(f"{release['codename']} is supported.") # Kernel should be ahead of EoL

                    break

            if not found:
                print('OS release not found in API') # Kernel may be either unsupported or new enough not to be found using the EoL api.

        await asyncio.sleep(1800)

#asyncio.run(outdated_os_check())


#print(url)
#response = requests.get(linux_url)
#response = response.json()
#print(response)
#asyncio.run(outdated_os_chech)

