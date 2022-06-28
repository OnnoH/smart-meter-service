import log
import sys

from paho.mqtt import client as mqtt

logger = log.get_logger(__name__)


def get_host(host):
    default_host = "localhost"
    if host is None:
        return default_host

    return host


def get_port(port):
    default_port = '1883'
    if port is None:
        return default_port

    return port


def get_topic(topic):
    default_topic = 'smart-meter'
    if topic is None:
        return default_topic

    return topic


def get_name(name):
    default_name = 'Smart_Meter'
    if name is None:
        return default_name

    return name


def get_protocol(protocol):
    default_protocol = 'MQTTv5'
    if protocol is None:
        return default_protocol

    return protocol


def get_transport(transport):
    default_transport = 'tcp'
    if transport is None:
        return default_transport

    return transport


def get_clean_session(clean_session):
    default_clean_session = False
    if clean_session is None:
        return default_clean_session

    if clean_session.lower() == 'true':
        return True
    else:
        return False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected as %s to MQTT Broker %s", client.name, client.broker)
    else:
        logger.error("Failed to connect to %s, return code %d", client.broker, rc)
        sys.exit("Error while opening %s. Program aborted." % client.name)


def on_disconnect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Disconnected as %s to MQTT Broker %s", client.name, client.broker)
    else:
        logger.error("Failed to connect to %s, return code %d", client.broker, rc)
        sys.exit("Error while opening %s. Program aborted." % client.name)


def on_message(client, userdata, msg):
    logger.debug(msg.topic+" "+str(msg.payload))


class MQTT:
    def __init__(self, config):
        self.name = get_name(config.get('name'))
        self.protocol = get_protocol(config.get('protocol'))
        self.transport = get_transport(config.get('transport'))
        self.cleanSession = get_clean_session(config.get('cleanSession'))
        self.url = get_host(config.get('broker'))
        self.port = get_port(config.get('port'))
        self.broker = self.url + ':' + self.port
        self.topic = get_topic(config.get('topic'))

        self.client = mqtt.Client(client_id=self.name, clean_session=self.clean_session, userdata=None, protocol=self.protocol, transport=self.transport)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message


    def publish_telegram(self, telegram):
        try:
            self.client.connect(self.broker)
            self.client.publish(self.topic, telegram)
            self.client.disconnect()

        except mqtt. as e:
            self.serial.close()
            logger.error("Error while opening %s. Program aborted." % self.name)
            sys.exit("Error while opening %s. Program aborted." % self.name)
        except TypeError as e:
            self.serial.close()
            sys.exit("Error while typing %s. Program aborted." % self.name)