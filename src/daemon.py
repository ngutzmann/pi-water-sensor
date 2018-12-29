# Python Imports
import atexit
import os
import signal
import sys
import time


class Daemon(object):
    '''A generic daemon class.
    Most of this was taken from:
    http://web.archive.org/web/20131017130434/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
    Usage: subclass the Daemon class and override the run() method
    '''

    def __init__(self, pid_file, stdin='/dev/null', stderr='/dev/null', stdout='/dev/null'):
        self.__pid_file = pid_file
        self.__stdin = stdin
        self.__stderr = stderr
        self.__stdout = stdout

    def _run(self):
        '''This method should be overridden when you subclassing Daemon.
        It will be called after the process has been daemonized by start()
        or restart().
        '''
        raise NotImplementedError('The run method must be implemented for subclasses of the Daemon class')

    def start(self):
        '''Start the daemon'''

        # Check for a pidfile to see if the daemon already runs
        pid = self.__read_pid_file()

        if pid:
            running = self.__test_proc(pid)
            if running:
                message = 'Daemon running (pid: %s)\n' % (pid)
                sys.stderr.write(message)
                sys.exit(1)
            else:
                message = 'pidfile %s exists, but pid %s is not active.\n' % (self.__pid_file, pid)
                message += 'Removing pidfile and launching daemon.\n'
                self.__del_pid()
                sys.stderr.write(message)

        # Start the daemon
        self.__daemonize()
        self._run()

    def check(self):
        '''Check if the daemon is running'''
        message = 'Daemon not running\n'
        pid = self.__read_pid_file()
        if pid:
            running = self.__test_proc(pid)
            if running:
                message = 'Daemon running (pid: %s)\n' % (pid)
            else:
                message = 'pidfile %s exists, but pid %s is not active.\n' % (self.__pid_file, pid)

        sys.stderr.write(message)

    def stop(self):
        '''Stop the daemon'''

        # Get the pid from the pidfile
        pid = self.__read_pid_file()
        if not pid:
            message = "pidfile %s does not exist. Daemon stopped?\n"
            sys.stderr.write(message % self.__pid_file)
            # not an error in a restart
            return

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGINT)
                time.sleep(1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.__pid_file):
                    os.remove(self.__pid_file)
            else:
                sys.stderr.write(str(err))
                sys.exit(1)

    def restart(self):
        '''Restart the daemon'''

        self.stop()
        self.start()

    def __daemonize(self):
        '''Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        '''
        # Do the first fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('Fork #1 Failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # Do the second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('Fork #2 Failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.__stdin, 'r')
        so = open(self.__stdout, 'a+')
        se = open(self.__stderr, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.__del_pid)
        pid = str(os.getpid())
        open(self.__pid_file, 'w+').write('%s\n' % (pid))

    def __del_pid(self):
        os.remove(self.__pid_file)

    def __read_pid_file(self):
        # Check for a pidfile to see if the daemon already runs
        pid = None
        try:
            pf = open(self.__pid_file, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        return pid

    def __test_proc(self, pid):
        # Sending signal 0 to a pid will raise OSError exception
        # if the pid is not running and do nothing otherwise
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True
