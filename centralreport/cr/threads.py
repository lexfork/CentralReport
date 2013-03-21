# -*- coding: utf-8 -*-

"""
    CentralReport - Threads module
        Contains threads used by CentralReport to perform periodic actions

    https://github.com/miniche/CentralReport/
"""

import datetime
import json
import threading
import time

from cr import collectors, webservices
from cr import log
from cr.entities import host
from cr.utils import text
from cr.utils.text import convert_text_to_bool
from cr.tools import Config


class Checks(threading.Thread):
    """
        Thread performing periodically checks.
    """

    hostEntity = None  # Get host informations

    # Last checks (with new entities classes)

    last_check_cpu = None
    last_check_date = None
    last_check_disk = None
    last_check_loadAverage = None
    last_check_memory = None

    performChecks = True  # True = perform checks...
    tickCount = 60  # Initial Count (Perform a check when starting)

    def __init__(self):
        threading.Thread.__init__(self)
        log.log_debug('ThreadChecks is starting...')  # Standard output

        # What is the current os?

        if Config.HOST_CURRENT == Config.HOST_MAC:
            self.MyCollector = collectors.MacCollector()
        elif (Config.HOST_CURRENT == Config.HOST_DEBIAN) or (Config.HOST_CURRENT == Config.HOST_UBUNTU):
            self.MyCollector = collectors.DebianCollector()

        # Perform a check every xx ticks (1 tick = 1 second)

        try:
            self.tickPerformCheck = int(Config.get_config_value('Checks', 'interval'))
        except:
            self.tickPerformCheck = 60

        log.log_debug('Interval between two checks: %s seconds' % self.tickPerformCheck)

        self.start()

    def run(self):
        """
            Executes checks.
        """

        # Getting informations about the current host

        Checks.hostEntity = self.MyCollector.get_infos()

        while Checks.performChecks:
            if self.tickPerformCheck <= self.tickCount:
                log.log_debug('---- New check -----')

                # Checking CPU
                log.log_debug('Doing a CPU check...')
                Checks.last_check_cpu = self.MyCollector.get_cpu()

                # Checking memory
                log.log_debug('Doing a memory check...')
                Checks.last_check_memory = self.MyCollector.get_memory()

                # Checking Load Average
                log.log_debug('Doing a load average check...')
                Checks.last_check_loadAverage = self.MyCollector.get_loadaverage()

                # Checking disks informations
                log.log_debug('Doing a disk check....')
                Checks.last_check_disk = self.MyCollector.get_disks()

                # Updating last check date...
                Checks.last_check_date = datetime.datetime.now()

                # TODO** Work on a better way to get disks
                all_disks = []

                for disk in Checks.last_check_disk.checks:
                    check_disk = {
                        'name': str.replace(disk.name, '/dev/', '').decode('utf-8'),
                        'free': text.convert_byte(disk.free),
                        'total': text.convert_byte(disk.size),
                        'percent': int(round(disk.used, 0) * 100 / int(disk.size))
                    }
                    all_disks.append(check_disk)

                myHost = host.Full()
                myHost.host = Checks.hostEntity

                myHost.cpu = Checks.last_check_cpu
                myHost.memory = Checks.last_check_memory
                myHost.load = Checks.last_check_loadAverage
                myHost.disks = json.dumps(all_disks)

                webservices.WebServices.send_full_check(myHost.json_serialize())

                # Wait 60 seconds before next checks...

                log.log_debug('All checks are done')
                log.log_debug('Next checks in %s seconds...' % self.tickPerformCheck)

                self.tickCount = 0

            # new tick

            self.tickCount += 1
            time.sleep(1)
