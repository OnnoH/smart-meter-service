# Smart Meter Service

(part of project Locutus, incubation stage)

## Introduction

In The Netherlands most households have a 'slimme meter'. A smart meter that shows consumption of gas and electricity. Interfacing with that device requires a P1 USB smart meter cable. Search the web for the best deal, but it'll set you back around fifteen euros.

And you also need some software of course, but luckily the web is filled with solutions regarding this matter. So if you're looking for integration with your Smart Home Controller, it's probably there.

I've decided to do the heavy lifting myself because it's fun. Of course I look for solutions that fellow developers have committed and build upon that. Furthermore there's no pressure, because my energy company provides me with a monthly report about my energy consumption ;-)

## Specification

Netbeheer Nederland is an association of network operators.

Here is a link to the [specifications](https://www.netbeheernederland.nl/dossiers/slimme-meter-15/documenten)

## The Code

At the moment the source code is not coherent. The idea is to have an HTTP endpoint available to get the readings and also sending them out via MQTT at a scheduled interval to allow for collection and database storage.

The entrypoint should be `p1-meter.py`.

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
