# -*- coding: utf-8 -*-
# Copyright (C) 2017 Daniel Marks
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import time
import logging
import logging.handlers
from tooz import coordination
from subprocess import Popen
from subprocess import PIPE
from threading import Thread


class Coordinator:
    """Coordination wrapper for arbitrary commands"""

    def __init__(self, options):
        self.options = options
        self.rc = 0

        # Configure logging
        self.logger = logging.getLogger('coolock')
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "information": logging.INFO,
            "warning": logging.WARNING,
            "warn": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
            "crit": logging.CRITICAL
        }
        self.logger.setLevel(levels[options.log_level])
        handler = logging.handlers.RotatingFileHandler(
            options.log_file, maxBytes=options.log_max_size, backupCount=options.rotate_log_copies)
        formatter = logging.Formatter('%(asctime)s - %(name)s (%(process)d) - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Configure coordination client
        self.logger.debug("Initializing coordination client for node: %s. Using: %s" %
                          (options.node, options.coordination_backend))
        self.coord_client = coordination.get_coordinator(
            options.coordination_backend, options.node)
        self.coord_client.start()
        self.lock = self.coord_client.get_lock(options.lock)

    def _execute_command(self):
        """Execute the command that is wrapped by coolock."""

        def stream_watchdog(stream_name, stream):
            """"Write the payload commands stdout and stderr to the main processes stdout and stderr"""
            for line in stream:
                if stream_name == 'STDOUT':
                    sys.stdout.write(line)
                elif stream_name == 'STDERR':
                    sys.stderr.write(line)
            if not stream.closed:
                stream.close()

        # Execute the payload command
        self.logger.debug("Executing command: %s" % self.options.command)
        proc = Popen(" ".join(self.options.command), stdout=PIPE, stderr=PIPE, shell=True)

        # Setup stdout and stderr redirection
        stdout_watchdog = Thread(target=stream_watchdog, name='stdout-watcher', args=('STDOUT', proc.stdout))
        stderr_watchdog = Thread(target=stream_watchdog, name='stderr-watcher', args=('STDERR', proc.stderr))
        stdout_watchdog.start()
        stderr_watchdog.start()

        # Wait for everything to finish
        proc.wait()
        stdout_watchdog.join()
        stderr_watchdog.join()

        # Check for errors
        if proc.returncode == 0:
            self.logger.info("The payload command executed successfully.")
        else:
            self.logger.error("The payload command returned an error code: %d. See command output for details."
                              % proc.returncode)

        return proc.returncode

    def run(self):
        """Start the coordinator and execute the wrapped command if the lock can be acquired."""
        _blocking = False if self.options.wait_timeout == 0 else self.options.wait_timeout
        self.logger.debug("Trying to acquire lock '%s'" % self.lock.name)

        # Try to acquire the lock
        if self.lock.acquire(blocking=_blocking):
            self.logger.info("Lock '%s' acquired." % self.lock.name)

            # Run payload command and record the execution time
            start = time.time()
            self.rc = self._execute_command()
            run_time = time.time() - start
            guard_time = self.options.guard_time

            # Release lock after guard_time has run out
            if run_time < guard_time:
                self.logger.debug(
                    "Sleeping %f s, because the commands run time (%f s) was shorter than the guard_time (%f s)."
                    % (guard_time - run_time, run_time, guard_time))
                time.sleep(guard_time - run_time)
            self.lock.release()
            self.logger.info("Lock '%s' released." % self.lock.name)
        else:
            self.logger.info("Did not acquire lock '%s'. Terminating." % self.lock.name)
            self.coord_client.stop()
