import configparser

config = configparser.ConfigParser()
config["PATHS"] = {
    "Logfile": "eolas.log",
    "Outfile": "SYSINFO.txt",
    "write_mode": "a",
}

config["SYSINFO"] = {
    "Disks": "True",
}
with open("config.ini", "w") as configfile:
    config.write(configfile)
