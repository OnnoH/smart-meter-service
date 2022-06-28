import crc16
import log
import re
import json

from time import mktime
from datetime import datetime

logger = log.get_logger(__name__)


def check_crc16(telegram):
    crc = 0
    for telegram_line in telegram:
        crc = crc16.crc16xmodem(telegram_line, crc)
    print(hex(crc))


class TelegramError(Exception):
    pass


class Telegram(object):
    _datagram = ''

    def __init__(self, datagram):
        self._datagram = datagram

        self.validate()

        keys = {}

        keys['header'] = self.get(r'^\s*(/.*)\r\n')
        keys['version'] = self.get_int(r'^1-3:0\.2\.8\((\d+)\)\r\n')

        timestamp = self.get(r'^0-0:1\.0\.0\((\d+)[SW]\)\r\n')
        if timestamp:
            keys['timestamp'] = int(mktime(datetime.strptime(timestamp, "%y%m%d%H%M%S").timetuple()))
        else:
            keys['timestamp'] = None

        keys['kwh'] = {}
        keys['kwh']['eid'] = self.get(r'^0-0:96\.1\.1\(([^)]+)\)\r\n')
        keys['kwh']['tariff'] = self.get_int(r'^0-0:96\.14\.0\(([0-9]+)\)\r\n')
        keys['kwh']['switch'] = self.get_int(r'^0-0:96\.3\.10\((\d)\)\r\n')
        keys['kwh']['threshold'] = self.get_float(r'^0-0:17\.0\.0\(([0-9]{4}\.[0-9]{2})\*kW\)\r\n')

        keys['kwh']['low'] = {}
        keys['kwh']['low']['consumed'] = self.get_float(r'^1-0:1\.8\.1\(([0-9]+\.[0-9]+)\*kWh\)\r\n')
        keys['kwh']['low']['produced'] = self.get_float(r'^1-0:2\.8\.1\(([0-9]+\.[0-9]+)\*kWh\)\r\n')

        keys['kwh']['high'] = {}
        keys['kwh']['high']['consumed'] = self.get_float(r'^1-0:1\.8\.2\(([0-9]+\.[0-9]+)\*kWh\)\r\n')
        keys['kwh']['high']['produced'] = self.get_float(r'^1-0:2\.8\.2\(([0-9]+\.[0-9]+)\*kWh\)\r\n')

        keys['kwh']['current_consumed'] = self.get_float(r'^1-0:1\.7\.0\(([0-9]+\.[0-9]+)\*kW\)\r\n')
        keys['kwh']['current_produced'] = self.get_float(r'^1-0:2\.7\.0\(([0-9]+\.[0-9]+)\*kW\)\r\n')

        keys['instantaneous'] = {}
        keys['instantaneous']['l1'] = {}
        keys['instantaneous']['l1']['volts'] = self.get_float(r'^1-0:32\.7\.0\((\d+\.\d+)\*V\)\r\n')
        keys['instantaneous']['l1']['amps'] = self.get_int(r'^1-0:31\.7\.0\((\d+)\*A\)\r\n')
        keys['instantaneous']['l1']['watts'] = self.get_float(r'^1-0:21\.7\.0\((\d+\.\d+)\*kW\)\r\n', 0) * 1000
        keys['instantaneous']['l2'] = {}
        keys['instantaneous']['l2']['volts'] = self.get_float(r'^1-0:52\.7\.0\((\d+\.\d+)\*V\)\r\n')
        keys['instantaneous']['l2']['amps'] = self.get_int(r'^1-0:51\.7\.0\((\d+)\*A\)\r\n')
        keys['instantaneous']['l2']['watts'] = self.get_float(r'^1-0:41\.7\.0\((\d+\.\d+)\*kW\)\r\n', 0) * 1000
        keys['instantaneous']['l3'] = {}
        keys['instantaneous']['l3']['volts'] = self.get_float(r'^1-0:72\.7\.0\((\d+\.\d+)\*V\)\r\n')
        keys['instantaneous']['l3']['amps'] = self.get_int(r'^1-0:71\.7\.0\((\d+)\*A\)\r\n')
        keys['instantaneous']['l3']['watts'] = self.get_float(r'^1-0:61\.7\.0\((\d+\.\d+)\*kW\)\r\n', 0) * 1000

        keys['gas'] = {}
        keys['gas']['eid'] = self.get(r'^0-1:96\.1\.0\(([^)]+)\)\r\n')
        keys['gas']['device_type'] = self.get_int(r'^0-1:24\.1\.0\((\d)+\)\r\n')
        keys['gas']['total'] = self.get_float(r'^(?:0-1:24\.2\.1(?:\(\d+[SW]\))?)?\(([0-9]{5}\.[0-9]{3})(?:\*m3)?\)\r\n', 0)
        keys['gas']['valve'] = self.get_int(r'^0-1:24\.4\.0\((\d)\)\r\n')

        measured_at = self.get(r'^(?:0-1:24\.[23]\.[01](?:\((\d+)[SW]?\))?)')

        if measured_at:
            keys['gas']['measured_at'] = int(mktime(datetime.strptime(measured_at, "%y%m%d%H%M%S").timetuple()))
        else:
            keys['gas']['measured_at'] = None

        keys['msg'] = {}
        keys['msg']['code'] = self.get(r'^0-0:96\.13\.1\((\d+)\)\r\n')
        keys['msg']['text'] = self.get(r'^0-0:96\.13\.0\((.+)\)\r\n')
        self._keys = keys

    def __getitem__(self, key):
        return self._keys[key]

    def get_float(self, regex, default=None):
        result = self.get(regex, None)
        if not result:
            return default
        return float(self.get(regex, default))

    def get_int(self, regex, default=None):
        result = self.get(regex, None)
        if not result:
            return default
        return int(result)

    def get(self, regex, default=None):
        results = re.search(regex, self._datagram, re.MULTILINE)
        if not results:
            return default
        return results.group(1)

    def validate(self):
        pattern = re.compile(r'\r\n(?=!)')
        for match in pattern.finditer(self._datagram):
            packet = self._datagram[:match.end() + 1]
            checksum = self._datagram[match.end() + 1:]

        if checksum.strip():
            given_checksum = int('0x' + checksum.decode('ascii').strip(), 16)
            calculated_checksum = crc16(packet)

            if given_checksum != calculated_checksum:
                logger.error('Checksum mismatch: given={}, calculated={}'.format(given_checksum, calculated_checksum))
                raise TelegramError('P1Packet with invalid checksum found')

    def __str__(self):
        return json.dumps(self._keys)

    def __dict__(self):
        return self._keys
