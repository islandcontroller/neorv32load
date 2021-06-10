# ------------------------------------------------------------------------------
# neorv32load
#
# Cross-platform compatible firmware download tool for use with the NEORV32
# bootloader.
# Targeted project: The NEORV32 RISC-V Processor by S. Nolting 
# (https://github.com/stnolting/neorv32)
#
#
# Copyright © 2021 islandc_
# https://github.com/islandcontroller/neorv32load/
#

import argparse
import serial

def process_args() -> argparse.Namespace:
  """Helper function to set up command line argument parser and process arguments

  Returns:
      argparse.Namespace: Processed options
  """
  parser = argparse.ArgumentParser(description='Script for uploading an application image via bootloader UART')
  parser.add_argument('port', type=str, help='Serial/COM port, as required for the host OS (e.g. \"/dev/ttyUSB0\", \"COM3\" etc.)')
  parser.add_argument('file', type=argparse.FileType('rb'), help='Application image in bootloader format (e.g. \"neorv32_exe.bin\")')
  parser.add_argument('-b', dest='baud', type=int, default=19200, help='Serial baud rate (defaults to 19200)')
  parser.add_argument('-t', dest='timeout', type=int, default=3, help='Line timeout in seconds (defaults to 3)')
  parser.add_argument('-v', action='store_true', help='Print verbose output')
  parser.add_argument('--keep', action='store_true', help='Keep port open after download and print RX')
  return parser.parse_args()

if __name__ == "__main__":
  device_ready: bool = False
  upload_ok: bool = False

  args: argparse.Namespace = process_args()

  with serial.Serial(port=args.port, baudrate=args.baud, timeout=args.timeout) as s:
    # Immediately try to enter upload mode
    print('Entering upload mode (sending \"#\")')
    s.write(b'#')

    # Wait until device is ready
    line = s.readline()
    while line:
      if args.v:
        print(line)
      if 'Bootloader' in str(line):
        print('Re-sending upload command')
        s.write(b'#')
      if 'neorv32_exe.bin' in str(line):
        device_ready = True
        break
      line = s.readline()

    # Evaluate wait result, abort if timeout
    if not device_ready:
      print('Aborting upload')
      exit()
    else:
      print('Starting upload')

    # Send binary file content
    d = args.file.read()
    s.write(d)
    print(f"{len(d)} bytes sent")
    s.flush()

    # Await upload ACK from device
    line = s.readline()
    while line:
      if args.v:
        print(line)
      if 'OK' in str(line):
        upload_ok = True
        break
      line = s.readline()

    # Evaluate wait result, abort if upload failed
    if not upload_ok:
      print('Upload failed')
      exit()
    else:
      print('Upload successful')

    # Optional: print serial RX until timeout
    if args.keep:
      print('Printing RX')
      line = s.readline()
      while line:
        print(line)
        line = s.readline()
      print('Closed')