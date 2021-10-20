import serial
import asyncio
import multiprocessing
import subprocess
import sys
import glob

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def setVolume(v):
    subprocess.call(["osascript", "-e set volume output volume "+ str(v)])
    return v

def scan():
    global prev, serialPort, process
    try:
        new = int(serialPort.readline())# + (-100)
        if prev != new:
            if type(process) is multiprocessing.Process:
                process.terminate()
            process = multiprocessing.Process(target=setVolume, args=(new,))
            process.start()
            prev = new
            subprocess.call(["clear"])
            t = ("🔇" if new == 0 else "🔊" if new > 70 else "🔉" if new > 40 else "🔈") + str(new)
            print(t)
    except Exception as e:
        print(e)

async def main():
    global serialPort
    while True:
        if (serialPort.in_waiting > 0):
            scan()

if __name__ == '__main__':
    prev = 0
    process = None

    ports = list(filter((lambda x: "usb" in x), serial_ports()))
    serial_com = ports[int(input("\n".join([str(i) + ": " + p for i, p in enumerate(ports)]) + "\nPort: "))]

    serialPort = serial.Serial(port = serial_com, baudrate=9600,
                                   bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    finally:
        loop.close()