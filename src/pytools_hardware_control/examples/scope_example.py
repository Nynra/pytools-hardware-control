from hhslablib.hardware.scope import TektronixScope
import pyvisa as visa


if __name__ == '__main__':
    # Create the VISA instance for the scope
    rm = visa.ResourceManager()

    # Scan wich devices are connected
    print(rm.list_resources())

    raise NotImplementedError("This example is not yet implemented.")
