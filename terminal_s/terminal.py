"""
Terminal for serial port

Requirement:

    + pyserial
    + colorama
    + py-getch
    + click
"""

import os
os.system('title Terminal S')

from collections import deque
import threading
import sys

import colorama
import click
from getch import getch
import serial
from serial.tools import list_ports


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-p', '--port', default=None, help='serial port name')
@click.option('-b', '--baudrate', default=115200, help='set baud reate')
@click.option('--parity', default='N', type=click.Choice(['N', 'E', 'O', 'S', 'M']), help='set parity')
@click.option('-s', '--stopbits', default=1, help='set stop bits')
@click.option('-l', is_flag=True, help='list serial ports')
def main(port, baudrate, parity, stopbits, l):
    if port is None:
        ports = list_ports.comports()
        if not ports:
            print('--- No serial port available ---')
            return
        if len(ports) == 1:
            port = ports[0][0]
        else:
            print('--- Available Ports ----')
            for i, v in enumerate(ports):
                print('---  {}: {}'.format(i, v))
            
            if l:
                return
            raw = input('--- Select port index: ')
            try:
                n = int(raw)
                port = ports[n][0]
            except:
                return
    try:
        device = serial.Serial(port=port,
                                baudrate=baudrate,
                                bytesize=8,
                                parity=parity,
                                stopbits=stopbits,
                                timeout=0.1)
    except:
        print('--- Failed to open {} ---'.format(port))
        return

    print('--- Press Ctrl+] to quit ---')

    queue = deque()
    
    def read_input():
        while device.is_open:
            ch = getch()
            # print(ch)
            if ch == b'\x1d':                   # 'ctrl + ]' to quit
                break
            if ch == b'\x00' or ch == b'\xe0':  # arrow keys' escape sequences
                ch2 = getch()
                conv = { b'H': b'A', b'P': b'B', b'M': b'C', b'K': b'D' }
                if ch2 in conv:
                    # Esc[
                    queue.append(b'\x1b[' + conv[ch2])
                else:
                    queue.append(ch + ch2)
            else:  
                queue.append(ch)

    colorama.init()

    thread = threading.Thread(target=read_input)
    thread.start()
    while thread.is_alive():
        try:
            length = len(queue)
            if length > 0:
                device.write(b''.join(queue.popleft() for _ in range(length)))

            line = device.readline()
            if line:
                print(line.decode(), end='', flush=True)
        except IOError:
            print('Device is disconnected')
            break
        except UnicodeDecodeError:
            print([x for x in line])

    device.close()


if __name__ == "__main__":
    main()
