"""
Terminal for serial port

Requirement:

    + pyserial
    + colorama
    + py-getch
    + click
"""

import os
if os.name == 'nt':
    os.system('title Terminal S')

from collections import deque
import sys
import threading

import colorama
import click
import serial
import datetime
from serial.tools import list_ports

# define our clear function
def screen_clear():
    # for windows
    if os.name == 'nt':
        os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        os.system('clear')


def run(port, baudrate, parity='N', stopbits=1):
    try:
        device = serial.Serial(port=port,
                                baudrate=baudrate,
                                bytesize=8,
                                parity=parity,
                                stopbits=stopbits,
                                timeout=0.1)
    except:
        print('--- Failed to open {} ---'.format(port))
        return 0

    print('--- {} is connected.---'.format(port))
    print('---Press Ctrl+] to quit---')
    print('---Press Ctrl+t to show or hide timestamp---')
    print('---Press Ctrl+l clear screen---')
    queue = deque()
    timestamp_en = bool()
    timestamp_input_en = bool()
    def read_input():
        nonlocal timestamp_en
        nonlocal timestamp_input_en
        if os.name == 'nt':
            from msvcrt import getch
        else:
            import tty
            import termios
            stdin_fd = sys.stdin.fileno()
            tty_attr = termios.tcgetattr(stdin_fd)
            tty.setraw(stdin_fd)
            getch = lambda: sys.stdin.read(1).encode()

        while device.is_open:
            ch = getch()
            # print(ch)
            if ch == b'\x1d':                   # 'ctrl + ]' to quit
                break
            if ch == b'\x0c':
                screen_clear()                  # 'ctrl + l' to clear screen
            if ch == b'\x14':                   # 'ctrl + t' to change timestamp status
                timestamp_en = bool(1-timestamp_en)
            if ch == b'\x00' or ch == b'\xe0':  # arrow keys' escape sequences for windows
                ch2 = getch()
                esc_dict = { b'H': b'A', b'P': b'B', b'M': b'C', b'K': b'D', b'G': b'H', b'O': b'F' }
                if ch2 in esc_dict:
                    queue.append(b'\x1b[' + esc_dict[ch2])
                else:
                    queue.append(ch + ch2)
                timestamp_input_en = False
            else:
                queue.append(ch)
                if ch == b' ' or ch == b'\n' or ch == b'\r':
                    timestamp_input_en = False
                elif ch == b'\x1b':            # arrow keys' escape sequences for linux
                    ch2 = getch()
                    if ch2 == b'[':
                        ch2 = getch()
                        esc_dict = { b'A': b'A', b'B': b'B', b'C': b'C', b'D': b'D', b'H': b'H', b'F': b'F' }
                        if ch2 in esc_dict:
                            queue.append(b'[' + esc_dict[ch2])
                        else:
                            queue.append(b'[' + ch2)
                    else:
                        queue.append(ch2)
                    timestamp_input_en = False
                else:
                    timestamp_input_en = True
                # print(queue)

        if os.name != 'nt':
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, tty_attr)

    colorama.init()

    thread = threading.Thread(target=read_input)
    thread.start()
    while thread.is_alive():
        try:
            length = len(queue)
            queue_bak = queue.copy()
            if length > 0:
                device.write(b''.join(queue.popleft() for _ in range(length)))

            line = device.readline()
            if line:
                if (line in queue_bak and len(line) == len(queue_bak)) or (timestamp_en == False or timestamp_input_en == False) or (line == b'\r' or line == b'\r\n'):
                    print(line.decode(errors='replace'), end='', flush=True)
                    if timestamp_en == True:
                        timestamp_input_en = True
                else:
                    time_now = datetime.datetime.now().strftime('%H:%M:%S.%f')
                    print('\033[1;35m ' + time_now + '\033[0m ' + line.decode(errors='replace'), end='', flush=True)
                if (b'login:' in line):
                    usrname = b'root\r\n';
                    #print(usrname)
                    device.write(usrname)
                if (b'Password:' in line):
                    password = b'CherryYoudao\r\n';
                    #print(password)
                    device.write(password)
        except IOError:
            print('--- {} is disconnected ---'.format(port))
            break

    device.close()
    if thread.is_alive():
        print('--- Press R to reconnect the device, or press Enter to exit ---')
        thread.join()
        if queue and queue[0] in (b'r', b'R'):
            return 1
    return 0




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
                print('---  {}: {} {}'.format(i, v[0], v[2]))
            if l:
                return
            raw = input('--- Select port index: ')
            try:
                n = int(raw)
                port = ports[n][0]
            except:
                return

    while run(port, baudrate, parity, stopbits):
        pass

if __name__ == "__main__":
    main()
