import serial
import time
import sys

# Python Class for using the E2019Q encoder
# loosely based on MATLAB code given by manufacturer
class RLS_E2019Q:
    def __init__(self, com="COM7", baudrate=9600):
        super().__init__()
        self.com = com
        self.br = baudrate
        self.encoder = serial
        self.connected = False
        self.connectEncoder()

    def connectEncoder(self):
        self.connected = False
        try:
            self.encoder = serial.Serial(self.com, self.br, timeout=10)
            self.connected = True
        except serial.serialutil.SerialException:
            print("Encoder not connected, check COM#")
        if self.connected:
            print("\nRLS Connected!")
        return self.connected  # return success of method

    def isConnected(self):
        return self.connected

    # Opens the connection with the encoder
    def open_con(self):
        try:
            self.encoder.open()
            print("Encoder open")
        except AttributeError:
            self.connectEncoder()
        except serial.SerialException:
            print("Encoder is already open")
            self.encoder.close()
            self.encoder.open()

    # Closes the connection with the encoder
    def close_con(self):
        try:
            self.encoder.close()
            print("Encoder closed")
        except AttributeError:
            self.connectEncoder()
        except serial.SerialException:
            print("Encoder is already closed")

    # Converts encoder's position to inches
    def convert_to_inches(self, data):
        con_data = (data * 50) / 25400
        return con_data

    # Converts encoder's position to mm
    def convert_to_mm(self, data):
        con_data = (data * 50) / 1000
        return con_data

    # Converts distance in from in to mm
    def convert_in_to_mm(self, data):
        return data * 25.4

    # Converts distance in from mm to in
    def convert_mm_to_in(self, data):
        return data / 25.4

    # Gets the encoder's position in um (not converted)
    def getEncPos(self, con_type=""):

        self.open_con()

        self.encoder.write("?".encode("utf-8"))
        try:
            position = int(
                "".join(
                    [i for i in self.encoder.read(8).decode("utf-8") if i.isnumeric()]
                )
            )
        except AttributeError:
            print("Encoder not connected, check COM#")
            return

        self.close_con()

        if con_type == "in":
            return self.convert_to_inches(position)
        elif con_type == "mm":
            return self.convert_to_mm(position)
        else:
            return position

    # Sets the encoders zero position
    def setZeroPos(self):
        self.open_con()
        try:
            self.encoder.write("z".encode("utf-8"))
            print("0 0 0 0 0 0 0 0")
        except:
            print("Encoder not connected, check COM#")
        self.close_con()

    def main(self):
        self.close_con()
        while True:
            input("Hit ENTER to zero")
            self.setZeroPos()

            input("Hit ENTER to print measurement")
            length = self.getEncPos("in")
            print(format(length, "6.3f"))
            print(
                "difference: "
                + format(self.convert_in_to_mm(length - 24.002), "5.3f")
                + " mm"
            )


if __name__ == "__main__":
    rls = RLS_E2019Q()
    rls.main()
