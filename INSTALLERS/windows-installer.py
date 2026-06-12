from scapy.all import *
import psutil
import subprocess
import platform
import winreg
from fastapi import FastAPI
import uvicorn

REG_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"

def get_device_info():
    return {
        "hostname": platform.node(),
        "ip_address": get_if_addr(conf.iface),
        "mac_address": get_if_hwaddr(conf.iface),
        "os_name": get_os_name(),
        "os_version": determine_channel(),
        "architecture": platform.machine(),
        "manufacturer": get_windows_manufacturer(),
        "model": get_windows_model(),
        "serial_number": get_windows_serial(),
        "form_factor": get_windows_form_factor(),
        "hdd_capacity": get_windows_hdd_info()['Size'],
        "hdd_available": get_windows_hdd_info()['FreeSpace'],
        "is_managed": True,
        "cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
        "virtual_memory": psutil.virtual_memory()._asdict()
    }



def get_os_name():
    return (f"{platform.system()} {platform.win32_ver()[0]}")



def get_windows_info():
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH) as key:
        return {
            "family": platform.win32_ver()[0],
            "release": winreg.QueryValueEx(key, "DisplayVersion")[0].lower(),
            "edition": winreg.QueryValueEx(key, "EditionID")[0].lower(),
        }



def determine_channel():
    info = get_windows_info()

    version = f"{info['family']}-{info['release']}"
    edition = info["edition"]

    if "iot" in edition and edition.endswith("s"):
        return f"{version}-iot-lts"

    if edition.endswith("s"):
        return f"{version}-e-lts"

    if "enterprise" in edition:
        return f"{version}-e"

    return f"{version}-w"



# UNTESTED
def get_windows_serial():
    # Command to get the BIOS serial number
    cmd = "Get-CimInstance Win32_BIOS | Select-Object SerialNumber | ConvertTo-Json"
    
    # Run the command and capture output
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)

    serial = json.loads(result.stdout)

    return serial


# UNTESTED
def get_windows_manufacturer():
    # Command to get the Device Manufacturer
    cmd = "Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer | ConvertTo-Json"

    # Run the command and capture output
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)

    manufacturer = json.loads(result.stdout)

    return manufacturer


# UNTESTED
def get_windows_model():
    # Command to get the Device Model
    cmd = "Get-CimInstance Win32_ComputerSystem | Select-Object Model | ConvertTo-Json"

    # Run the command and capture output
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)

    model = json.loads(result.stdout)

    return model


# UNTESTED
def get_windows_form_factor():
    # Command to get the System Type (form factor)
    cmd = "Get-CimInstance Win32_SystemEnclosure | Select-Object ChassisTypes | ConvertTo-Json"

    # Run the command and capture output
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)

    form_factor = json.loads(result.stdout)

    return form_factor



def get_windows_hdd_info():
    GB = 1024 ** 3
    # Command to get HDD information (capacity and available space)
    cmd = "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID, Size, FreeSpace | ConvertTo-Json"

    # Run the command and capture output
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)
    
    drives = json.loads(result.stdout)

    # Unsure about how to implement this
    # PowerShell returns dict for single item, list for multiple
    #if isinstance(drives, dict):
    #    drives = [drives]

    drives['Size'] = str(round(drives['Size']/GB,1)) + " GB"
    drives['FreeSpace'] = str(round(drives['FreeSpace']/GB, 1)) + " GB"

    return drives


if __name__ == "__main__":
    pass