#!/usr/bin/python

"""PyWiiLoad Copyright (C) 2012 Bryan Cuneo
  This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
________________________________________________________________________

PyWiiLoad is a rewrite of wiiload.py.  I've added error handling, a
usage message if run with no arguments, a README file, automatic zipping
of directories, and the option to enter the IP address if the $WIILOAD
isn't set.  The code is now PEP8 compliant.  It has also been
reformatted into functions.  I felt this was necessary with all the extra
code that I added.

Original wiiload.py (author unknown): http://pastebin.com/4nWAkBpw

"""

import os
import platform
import socket
import struct
import sys
import zipfile
import zlib

# Required to send to the HBC
WIILOAD_VERSION_MAJOR = 0
WIILOAD_VERSION_MINOR = 5

# Get the version of Python this program is running under.
python_version = platform.python_version_tuple()

def getIP():
    """Obtain the Wii's IP address from the $WIILOAD environment variable.

    """
    ip = os.getenv("WIILOAD")
    if ip is None:
        set_ip = "i"
        while set_ip.lower() not in ["y", "yes", "n", "no"]:

            if python_version[0] == "3":
                set_ip = input("$WIILOAD is not set. Would you like to set it "
                               "temporarily? [y/n]: ")
            else:
                set_ip = raw_input("WIILOAD is not set. Would you like to set "
                                   "it temporarily+ [y/n]: ")
        if set_ip.lower() in ["n", "no"]:
            print("\nGoodbye.")
            exit()
        else:
            if python_version[0] == "3":
                ip = "tcp:" + input("Please enter your Wii's IP address "
                                    "(i.e. 192.168.1.106): ")
            else:
                ip = "tcp:" + raw_input("Please enter your Wii's IP address "
                                        "(i.e. 192.168.1.106): ")
            print("\n")
    try:
        assert ip.startswith("tcp:")
    except:
        print("$WIILOAD doesn't start with 'tcp:'")
        exit()

    return ip


def getFile(path):
    """Make sure it's possible to send the file/dir that the user provides.

    """
    if os.path.exists(path) is False:
        print(path + " doesn't seem to exist.  Please try again.")
        exit()

    if os.path.isdir(path):
        print("PyWiiLoad can't send a directory.  Only executables (.dol/.elf)"
              " and zip archives.")
        zip_or_not = "i"
        while zip_or_not.lower() not in ["y", "yes", "n", "no"]:
            if python_version[0] == "3":
                zip_or_not = input("Would you like to zip this directory and "
                                   "send it? [y/n]: ")
            else:
                zip_or_not = raw_input("Would you like to zip this directory "
                                       "and send it? [y/n]: ")
            if zip_or_not.lower() in ["n", "no"]:
                print("\nGoodbye.")
                exit()
            else:
                file = zip(path)
    else:
        file = path
        ext = os.path.splitext(file)
        if ext[1] not in [".dol", ".elf", ".zip"]:
            print("File type is not supported.  Must be .dol, .elf, or "
                  ".zip.")
                  ".zip.")
            exit()

    return file


def connect(ip_string, wii_ip, args, c_data, file):
    """Connect to the Wii.

    """
    print("Connecting to " + ip_string.lstrip("tcp:") + "...")
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect(wii_ip)
    except socket.error as e:
        print("Can't connect to the Wii:")
        print(e)
        print("\nConfirm your IP address, make sure that your Wii is on, "
              "connected to the Internet, and the\nHomebrew Channel is open.")
        exit()
    print("Connection successful.\n")

    if python_version[0] == "3":
        conn.send(bytes("HAXX", "utf8"))
    else:
        conn.send("HAXX")
    conn.send(struct.pack("B", WIILOAD_VERSION_MAJOR))  # one byte, unsigned
    conn.send(struct.pack("B", WIILOAD_VERSION_MINOR))  # one byte, unsigned
    conn.send(struct.pack(">H", len(args)))  # bigendian, 2 bytes, unsigned
    conn.send(struct.pack(">L", len(c_data)))  # bigendian, 4 bytes, unsigned
    conn.send(struct.pack(">L", os.path.getsize(file)))  # bigendian, 4
                                                         # unsigned

    return conn


def send(chunks, conn, args):
    """Send the file.

    """
    print("Sending " + str(len(chunks)) + " pieces...")
    num = 0
    for piece in chunks:
        conn.send(piece)
        num += 1
        sys.stdout.write(str(num))
        if num != len(chunks):
            sys.stdout.write(", ")
            sys.stdout.flush()
    if python_version[0] == "3":
        conn.send(bytes(args, "utf8"))
    else:
        conn.send(args)
    conn.close()


def zip(path):
    """Create a .zip archive if the user wants to send a directory.

    """
    split_path = os.path.split(path)
    folder = split_path[1]
    # Change the wd to the parent of the forder to be zipped.
    os.chdir(split_path[0])
    print("Zipping " + folder + "...")
    zip_deflated = zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile(folder + ".zip", mode="w", compression=zip_deflated)
    parent = os.path.split(folder)
    for dirpath, dirs, files in os.walk(folder):
        for f in dirs + files:
            zf.write(os.path.join(dirpath, f))
    zf.close()
    file = path.rstrip("/") + ".zip"
    print("Done.\n")

    return file



def main():
    """The main function (duh).

    """
    # Check if the first argument is a valid file or directory.  If not,
    # print a usage message and exit.
    try:
        sys.argv[1]
    except:
        print("""Usage:
./wiiload.py /path/to/boot.dol
./wiiload.py /path/to/boot.elf
./wiiload.py /path/to/appname.zip
./wiiload.py /path/to/appname/""")
        exit()

    # Print a short copyright notice when the program is run.
    print("""PyWiiLoad  Copyright (C) 2012 Bryan Cuneo
This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to use, modify, and redistribute it under the terms
of the GPLv3+.\n""")

    # Get the Wii's IP address and the file to send.
    ip_string = getIP()
    file = getFile(sys.argv[1])

    wii_ip = (ip_string[4:], 4299)

    # Compress the file and get it ready to send.
    if python_version[0] == "3":
        c_data = zlib.compress(open(file, "rb").read())
    else:
        c_data = zlib.compress(open(file).read())
    chunk_size = 1024 * 128
    chunks = [c_data[i:i + chunk_size] for i in range(0, len(c_data),
                                                      chunk_size)]

    args = [os.path.basename(file)] + sys.argv[2:]
    args = "\x00".join(args) + "\x00"

    # Connect to the Wii and send the file.
    conn = connect(ip_string, wii_ip, args, c_data, file)
    send(chunks, conn, args)

    # Print a parting message.             mmmmmmm
    print("\nDone.\n\nThank you for using PyWiiLoad!")


if __name__ == "__main__":
    main()
