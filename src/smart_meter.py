import log
import re
import serial
import sys

from crc16 import calculate_crc16

logger = log.get_logger(__name__)


def get_byte_size(bytesize):
    if bytesize is None:
        return serial.EIGHTBITS
    if bytesize == 5:
        return serial.FIVEBITS
    if bytesize == 6:
        return serial.SIXBITS
    if bytesize == 7:
        return serial.SEVENBITS

    return serial.EIGHTBITS  # default


def get_stop_bits(stopbits):
    if stopbits is None:
        return serial.STOPBITS_ONE
    if stopbits == 1.5:
        return serial.STOPBITS_ONE_POINT_FIVE
    if stopbits == 2:
        return serial.STOPBITS_TWO

    return serial.STOPBITS_ONE  # default


def get_parity_bit(parity):
    default_parity = serial.PARITY_NONE
    if parity is None:
        return default_parity
    if parity.upper() == 'EVEN':
        return serial.PARITY_EVEN
    if parity.upper() == 'ODD':
        return serial.PARITY_ODD
    if parity.upper() == 'MARK':
        return serial.PARITY_MARK
    if parity.upper() == 'SPACE':
        return serial.PARITY_SPACE

    return default_parity


def get_baudrate(baudrate):
    default_baudrate = 9600
    baudrates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 28800,
                 38400, 57600, 76800, 115200, 230400, 460800, 576000, 921600]
    if baudrate is None:
        return default_baudrate
    if baudrate in baudrates:
        return baudrate
    else:
        return default_baudrate


def get_xonxoff(xonxoff):
    default_xonxoff = False
    if xonxoff is None:
        return default_xonxoff
    if xonxoff.upper("True"):
        return True

    return default_xonxoff


def get_rtscts(rtscts):
    default_rtscts = False
    if rtscts is None:
        return default_rtscts
    if rtscts.upper("True"):
        return True

    return default_rtscts


def get_timeout(timeout):
    default_timeout = 12
    if timeout is None:
        return default_timeout

    return timeout


def get_dsrdtr(dsrdtr):
    default_dsrdtr = False
    if dsrdtr is None:
        return default_dsrdtr
    if dsrdtr.upper("True"):
        return True

    return default_dsrdtr


def get_name(name):
    default_name = "Generic Smart Meter"
    if name is None:
        return default_name

    return name


def get_port(port):
    default_port = None
    if port is None:
        return default_port

    return port


class SmartMeter:
    def __init__(self, config):
        self.name = get_name(config.get('name'))
        self.serial = serial.Serial()
        self.serial.port = get_port(config.get('port'))
        self.serial.baudrate = get_baudrate(config.get('baudrate'))
        self.serial.bytesize = get_byte_size(config.get('bytesize'))
        self.serial.stopbits = get_stop_bits(config.get('stopbits'))
        self.serial.parity = get_parity_bit(config.get('parity'))
        self.serial.xonxoff = get_xonxoff(config.get('xonxoff'))
        self.serial.rtscts = get_rtscts(config.get('rtscts'))
        self.serial.dsrdtr = get_dsrdtr(config.get('dsrdtr'))
        self.serial.timeout = get_timeout(config.get('timeout'))
        self.telegram = None
        self.checksum = None

    def get_telegram(self):
        telegram = ""
        start_telegram = False
        checksum_found = False

        try:
            self.serial.open()
            while not checksum_found:
                telegram_line = self.serial.readline()
                if re.match(b'(?=/)', telegram_line):
                    start_telegram = True
                if start_telegram:
                    if re.match(b'(?=!)', telegram_line):
                        self.checksum = int(telegram_line.decode()[1:], 16)
                        checksum_found = True
                        telegram += '!'
                    else:
                        telegram += telegram_line.decode()
            self.telegram = telegram
            self.serial.close()

            return telegram

        except serial.SerialException as e:
            self.serial.close()
            logger.error("Error while opening %s. Program aborted." % self.name)
            sys.exit("Error while opening %s. Program aborted." % self.name)
        except TypeError as e:
            self.serial.close()
            sys.exit("Error while typing %s. Program aborted." % self.name)

    def check_checksum(self):
        if self.telegram is None or self.checksum is None:
            return False
        return self.checksum == calculate_crc16(self.telegram)
