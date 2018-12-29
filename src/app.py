#!/usr/bin/env python

# Python Imports
from logging.config import dictConfig
import argparse
import logging
import sys

# App Module Imports
from daemon import Daemon
from config import LOG_CONFIG


class WaterSensorApp(Daemon):

    PID_FILE = '/tmp/water-sensor.pid'

    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(WaterSensorApp, self).__init__(self.PID_FILE, stdin, stdout, stderr)
        self._logger = logging.getLogger(type(self).__name__)

    def _run(self):
        dictConfig(LOG_CONFIG)
        self.__logger.info("Starting sensor")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IOT Water Sensor App')
    parser.add_argument('action', help='start|stop|restart')
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    stderr = '/dev/null'
    stdout = '/dev/null'

    if args.debug:
        stderr = '/dev/stderr'
        stdout = '/dev/stdout'

    daemon = WaterSensorApp(stderr=stderr, stdout=stdout)

    if 'start' == args.action:
        daemon.start()
    elif 'stop' == args.action:
        daemon.stop()
    elif 'restart' == args.action:
        daemon.restart()
    elif 'status' == args.action:
        daemon.check()
    else:
        sys.stderr.write('Unknown action: %s valid choices: start|stop|restart\n' % (args.action))
