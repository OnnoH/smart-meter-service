# Smart Meter Service
(work in progress)

## Introduction

In The Netherlands most households have a 'slimme meter'. A smart meter that shows consumption of gas and electricity.

## Specification

Netbeheer Nederland is an association of network operators.

Here is a link to the [specifications](https://www.netbeheernederland.nl/dossiers/slimme-meter-15/documenten)

## Culprits

Having Python 2.x and 3.x on the same system might confuse the interpreter which library to use

```
$ ls -l $(which python pip python2 pip2 python3 pip3)

$ sudo apt-get install python3
$ sudo apt-get install python3-pip

$ sudo pip uninstall pyserial pyyaml
$ sudo pip3 install pyserial pyyaml
```

## Credits

Converted the CRC16 code from JavaScript (https://github.com/jeroen13/p1-smart-meter-crc16), because [pycrc16](https://pypi.org/project/crc16/) used the wrong base table (xmodem) values. See also (https://pycrc.org/pycrc.html)

The lookup table variable is generated using pycrc =>
```
$ PYCRC="python pycrc.py --model crc-16 --algorithm table-driven --generate table"
$ echo "crc_arc_table = $(eval ${PYCRC} | tr "{}" "[]")"
```
Another source of inspiration is [Nico Di Rocco](https://github.com/nrocco)'s [smeterd](https://github.com/nrocco/smeterd)
