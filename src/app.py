#!/usr/bin/env python

# Python Imports
from datetime import datetime, timedelta
from logging.config import dictConfig
import argparse
import atexit
import logging
import os
import signal
import sys

# Third Party Imports
from gpiozero import DigitalInputDevice
import requests

# App Module Imports
from config import LOG_CONFIG
from daemon import Daemon


class WaterSensorApp(Daemon):

    PID_FILE = "/tmp/water-sensor.pid"

    HYSTERESIS = timedelta(hours=6)

    def __init__(self, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
        super(WaterSensorApp, self).__init__(self.PID_FILE, stdin, stdout, stderr)
        self.__logger = logging.getLogger(type(self).__name__)
        self.__hub = ""
        self.__client_id = ""
        self.__sensor = None
        self.__last_alert = datetime.min

    def _run(self):
        if not self.__hub:
            self.__logger.error("Missing `hub` configuration.")
            sys.exit(1)
        if not self.__client_id:
            self.__logger.error("Missing `client_id` configuration.")
            sys.exit(1)

        self.__initialize()
        signal.pause()

    @property
    def hub(self):
        return self.__hub

    @hub.setter
    def hub(self, hub):
        self.__hub = hub

    @property
    def client_id(self):
        return self.__client_id

    @client_id.setter
    def client_id(self, client_id):
        self.__client_id = client_id

    def __handle_water_detected(self):
        self.__logger.info("Detected water, alerting!")
        now = datetime.now()
        if (now - self.__last_alert) > self.HYSTERESIS:
            self.__last_alert = now
            requests.post(self.__hub, data={"client": self.__client_id})

    def __initialize(self):
        self.__logger.info("Starting sensor.")
        self.__sensor = DigitalInputDevice(4, pull_up=True)
        self.__sensor.when_activated = self.__handle_water_detected
        atexit.register(self.__cleanup)

    def __cleanup(self):
        self.__logger.info("Stopping sensor.")
        self.__sensor.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IOT Water Sensor App")
    parser.add_argument("action", help="start|stop|restart")
    parser.add_argument("-s", "--serverlessHub", help="The URL of the serverless hub")
    parser.add_argument(
        "-c", "--client", help="The specific ID of the client connecting to the hub"
    )
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()

    stderr = os.devnull
    stdout = os.devnull

    dictConfig(LOG_CONFIG)

    if args.debug:
        stderr = sys.stderr
        stdout = sys.stdout

    daemon = WaterSensorApp(stderr=stderr, stdout=stdout)

    if "start" == args.action:
        daemon.hub = args.serverlessHub
        daemon.client_id = args.client
        daemon.start()
    elif "stop" == args.action:
        daemon.stop()
    elif "restart" == args.action:
        daemon.restart()
    elif "status" == args.action:
        daemon.check()
    else:
        sys.stderr.write(
            "Unknown action: %s valid choices: start|stop|restart\n" % (args.action)
        )
