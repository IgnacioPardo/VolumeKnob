import serial
import asyncio
import multiprocessing
import subprocess
import sys
import glob
import json
import applescript

def setVolume(v):
    subprocess.call(["osascript", "-e set volume output volume "+ str(v)])
    return v

def inc_SC(n=1):
    applescript.tell.app('System Events', 'tell process "SoundSource" to perform action "AXIncrement" of slider 1 of UI element '+str(n)+' of window 1')

def dec_SC(n=1):
    applescript.tell.app('System Events', 'tell process "SoundSource" to perform action "AXDecrement" of slider 1 of UI element '+str(n)+' of window 1')

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def set_TB_Vol(v):
    v = translate(v, 0, 100, -16, 16)
    applescript.tell.app('System Events', 'tell process "Tonebridge Guitar Effects" to tell window "Tonebridge Guitar Effects" to tell splitter group 1 to set value of slider 2 to '+str(v))

def set_TB_FX(v):
    v = translate(v, 0, 100, -16, 16)
    applescript.tell.app('System Events', 'tell process "Tonebridge Guitar Effects" to tell window "Tonebridge Guitar Effects" to tell splitter group 1 to set value of slider 1 to '+str(v))


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

def scan_for_audio():
    global prevA, serialPort, process
    try:
        new = int(serialPort.readline())# + (-100)
        if prevA != new:
            if type(process[0]) is multiprocessing.Process:
                process[0].terminate()
            process[0] = multiprocessing.Process(target=setVolume, args=(new,))
            process[0].start()
            prevA = new
            subprocess.call(["clear"])
            t = ("🔇" if new == 0 else "🔊" if new > 70 else "🔉" if new > 40 else "🔈") + str(new)
            print(t)
    except Exception as e:
        print(e)

def scan_for_SC():
    global prev_SC, serialPort, process

    sliders = {    
                "0": 1,
                "1": 2,
                "2": 5,
                "3": 7
            }
    try:
        r = json.loads(serialPort.readline())# + (-100)
        if r.values() != prev_SC.values:
            subprocess.call(["clear"])
            for p, v in r.items():
                v = int(v)
                if v >= prev_SC[p]+7:
                    inc_SC(sliders[p])
                    prev_SC[p] = v
                elif v <= prev_SC[p]-7:
                    dec_SC(sliders[p])
                    prev_SC[p] = v
                t = ("🔇" if v == 0 else "🔊" if v > 70 else "🔉" if v > 40 else "🔈") + str(v)
                print(p+":  ", t)
    except Exception as e:
        print(e)

def scan_for_TB():
    global prev_TB, serialPort, process

    sliders = {    
                "0": 1,
                "1": 2,
            }
    slider_func = {    
                "0": set_TB_FX,
                "1": set_TB_Vol,
            }
    slider_emoji = {    
                "0": ["💔 ", "❤️‍🩹 ", "❤️ ", "❤️‍🔥 "],
                "1": ["🔇", "🔊", "🔉", "🔈"]
            }
    try:
        r = json.loads(serialPort.readline())# + (-100)
        if r.values() != prev_TB.values:
            subprocess.call(["clear"])
            for p, v in list(r.items())[:2]:
                v = int(v)
                if v != prev_TB[p]:
                    pr = int(p)
                    if type(process[pr]) is multiprocessing.Process:
                        process[pr].terminate()
                    process[pr] = multiprocessing.Process(target=slider_func[p], args=(v,))
                    process[pr].start()
                    prev_TB[p] = v
                t = (slider_emoji[p][0] if v == 0 else slider_emoji[p][3] if v > 70 else slider_emoji[p][2] if v > 40 else slider_emoji[p][1]) + str(v)
                print(p+":  ", t)
    except Exception as e:
        print(e)

async def main():
    global serialPort
    while True:
        if (serialPort.in_waiting > 0):
            scan_for_TB()

if __name__ == '__main__':
    prev_A = -1
    prev_SC =  {    
                "0": 100,
                "1": 100,
                "2": 100,
                "3": 100
            }
    prev_TB =  {    
                "0": 100,
                "1": 100,
            }
    process = [None, None, None, None]

    ports = list(filter((lambda x: "usb" in x), serial_ports()))
    serial_com = ports[0]
    if len(ports) > 1:
        serial_com = ports[int(input("\n".join([str(i) + ": " + p for i, p in enumerate(ports)]) + "\nPort: "))]

    serialPort = serial.Serial(port = serial_com, baudrate=9600,
                                   bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    finally:
        loop.close()