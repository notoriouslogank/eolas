import configparser
import logging
import subprocess
from datetime import datetime
from os import path
from pathlib import Path

import wmi

configfile = "config.ini"
disk_free = []


def make_config():
    config = configparser.ConfigParser()
    config["eolas"] = {
        "logfile": "eolas.log",
        "outfile": "sysinfo.txt",
        "write_mode": "a",
        "show_disk_free": "True",
        "show_sys_info": "True",
        "show_gpu_info": "True",
    }
    with open(configfile, "w") as ini:
        config.write(ini)
    logging.debug(f"Wrote config.ini.")


def default_config(configfile):
    with open(configfile, "a") as config:
        config.write(configfile)


def check_config():
    timestamp = datetime.now()
    if path.exists(configfile):
        logging.info(f"{timestamp} - Found configfile: {configfile}")
        return 1
    else:
        logging.info(f"{timestamp} - No configfile found; using default config.")
        #        default_config()
        return 0


def get_disk_list():
    timestamp = datetime.now()
    logging.info(f"{timestamp} - Getting disk_list.")
    output = subprocess.check_output(["wmic", "logicaldisk", "get", "name"]).decode(
        "utf-8"
    )
    new = output[5:].splitlines()
    disks = "".join(new).replace(" ", "").replace(":", "")
    disk_list = [i for i in disks]
    logging.debug(f"{timestamp} - Disk list: {disk_list}")
    logging.info(f"{timestamp} - Got disk list.")
    return disk_list


def get_disk_free():
    timestamp = datetime.now()
    logging.info(f"{timestamp} - Getting disk freespace...")
    disks = get_disk_list()
    for i in disks:
        output = subprocess.check_output(
            ["fsutil", "volume", "diskfree", f"{i}:"]
        ).decode("utf-8")
        logging.debug(f"{timestamp} - Freespace for {i}: {output}")
        disk_free.append(f"{i}:\r{output}")
    write_outfile(f"[DISKS]")
    for item in disk_free:
        clean_entry(item)
        write_outfile(item)
    logging.info(f"{timestamp} - Wrote disk free space.")


def get_sys_info():
    timestamp = datetime.now()
    logging.info(f"{timestamp} - Getting system information.")
    raw_info = subprocess.check_output(["systeminfo"]).decode("utf-8").split(f"\n")
    info_dump = []
    write_outfile(f"[SYSINFO]")
    for item in raw_info:
        info_dump.append(str(item.split("\r")[:-1]))
    for entry in info_dump:
        entry = clean_entry(entry)
        write_outfile(entry)
    logging.info(f"{timestamp} - Wrote system information.")


def get_gpu():
    timestamp = datetime.now()
    logging.info(f"{timestamp} - Getting GPU information.")
    controllers = wmi.WMI().Win32_VideoController()
    write_outfile("[GPU]")
    for controller in controllers:
        controller_info = {"Name": controller.wmi_property("Name").value}
        write_outfile(f"{controller_info['Name']}")
    logging.info(f"{timestamp} - Wrote GPU info.")


def clean_entry(entry):
    timestamp = datetime.now()
    cleaned_entry = (str(entry).strip("['\"]")).strip()
    cleaned_entry = " ".join(cleaned_entry.split())
    logging.debug(f"{timestamp} - Sanitizing entry {entry}")
    return cleaned_entry


def write_outfile(line):
    timestamp = datetime.now()
    config = configparser.ConfigParser()
    config.read(configfile)
    outfile = config["eolas"]["outfile"]
    write_mode = config["eolas"]["write_mode"]
    logging.debug(
        f"{timestamp} - Writing outfile: {outfile} in write_mode: {write_mode}"
    )
    with open(outfile, write_mode) as output:
        output.write(line)
        output.write("\r")
        logging.debug(f"{timestamp} - Wrote outfile.")


def email_outfile():
    timestamp = datetime.now()
    pass


def main():
    timestamp = datetime.now()
    configfile = "config.ini"
    disk_free = []
    logging.basicConfig(
        filename="eolas.log", filemode="w", encoding="utf-8", level=logging.INFO
    )

    logging.info(f"{timestamp}: Program start.")
    if check_config() == 0:
        default_config(configfile)
        make_config()
    get_sys_info()
    get_disk_free()
    get_gpu()
    logging.info(f"{timestamp}: Done.")


main()
