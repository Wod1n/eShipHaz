import os
import pytz
import calendar
from pyargon2 import hash
from datetime import datetime

def milDTG():
    if datetime.now().day < 10:
        dtg = '0' + str(datetime.now().day)
    else:
        dtg = str(datetime.now().day)

    if datetime.now().hour < 10:
        dtg = dtg + '0' + str(datetime.now().hour)
    else:
        dtg = dtg + str(datetime.now().hour)

    if datetime.now().minute < 10:
        dtg = dtg + '0' + str(datetime.now().minute)
    else:
        dtg = dtg + str(datetime.now().minute)

    timeZone = datetime.now().hour - datetime.now(pytz.utc).hour
    if timeZone < 0:
        timeZone = -1*timeZone + 12

    zoneCode = ['Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

    dtg = dtg + zoneCode[timeZone] + calendar.month_abbr[datetime.now().month] + str(datetime.now().year)
    return dtg

def milDTG(day, month, year, hour, minute, zone):
    zoneCode = ['Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

    if day < 10:
        dtg = '0' + str(day)
    else:
        dtg = str(day)

    if hour < 10:
        dtg = dtg + '0' + str(hour)
    else:
        dtg = dtg + str(hour)

    if minute < 10:
        dtg = dtg + '0' + str(minute)
    else:
        dtg = dtg + str(minute)

    dtg = dtg + zoneCode[zone] + calendar.month_abbr[month] + str(year)
    return dtg

def reverseMonth(abbr):
    lookup = {month: index for index, month in enumerate(calendar.month_abbr) if month}
    return lookup[abbr]

def hashPassword(password):
    salt = "Horse, Battery, Staple"
    return hash(password, salt)

def actArchive(arcLine):
    if not os.path.isdir("Archive"):
        os.mkdir("./Archive")

    fileName = "./Archive/"
    fileName = fileName + str(datetime.now().year) + " "
    fileName = fileName + calendar.month_name[datetime.now().month] + ".csv"

    if not os.path.isfile(fileName):
        file = open(fileName, "w")
        file.write("ShipHaz Line|Time put in Force|Work Sponsor|Authorising Officer|Time Removed|Removed By\n")
        file.write(arcLine)
        file.close()
    else:
        file = open(fileName, "a")
        file.write(arcLine)
        file.close()
