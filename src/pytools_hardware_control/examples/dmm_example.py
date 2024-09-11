from hhslablib.hardware.dmm import TTI1604
import pyvisa as visa


if __name__ == '__main__':
    config = {
        "serial_port": "/dev/ttyUSB0",
    }
    dmm = TTI1604(**config)

    while True:
        print(dmm.get_value())