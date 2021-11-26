import socket
import errno
import time
import select
import argparse
import sys
from collections import namedtuple, deque

SocketData = namedtuple("SocketData", ['sock', 'ip_address', 'port', 'start_time'])
ResultData = namedtuple("ResultData", ['ip_address', 'port', 'result_code'])


class ScannerError(Exception):
    pass


class ScanResultCode(object):
    OPEN, REFUSED, NO_ANSWER, ERROR, IN_PROGRESS = range(101, 106)
    MESSAGE = {
        OPEN: "Open",
        REFUSED: "Connection refused",
        NO_ANSWER: "Filtered",
        ERROR: "Unknown",
        IN_PROGRESS: "In progress"
    }


class PortScanner(object):
    DEFAULT_TIMEOUT = 1
    DEFAULT_RETRIES = 5

    def __init__(self, ip_address, start_port=1, end_port=65535, timeout=-1, num_retries=-1):
        if start_port > end_port:
            raise ValueError("Start port must be less than end port")
        self._start_port = start_port
        self._end_port = end_port
        self._ip_address = ip_address
        self._timeout = self.DEFAULT_TIMEOUT
        self._num_retries = self.DEFAULT_RETRIES

        self._init_running_data()

        if timeout > 0:
            self._timeout = timeout

        if num_retries > 0:
            self._num_retries = num_retries

    def _init_running_data(self):
        self._port_queue = range(self._start_port, self._end_port + 1)
        self._in_progress = {}
        self._results = []
        self._retries = {}

    def scan_ports(self):
        """scans """
        self._init_running_data()
        while self._port_queue or self._in_progress:
            self._do_scan_ports()
            self._check_sockets()

        self._results.sort()
        return self._results

    def _do_scan_ports(self):
        """Initializes a connection to a port; retry it later if a problem occurs"""
        port = self._port_queue.pop(0)
        scan_return = self._scan_ip_port(port)
        if not scan_return:
            self._port_queue.append(port)


    def _scan_ip_port(self, port):
        try:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            if e.errno == errno.EMFILE:
                return False
            new_socket.close()
            raise

        new_socket.setblocking(1)
        status = self._start_socket(new_socket, port)
        if status == ScanResultCode.IN_PROGRESS:
            print 'Unexpected error while creating socket to {}:{}, retrying.'.format(self._ip_address, port)
            return False
        self._add_in_progress(SocketData(new_socket, self._ip_address, port, time.time()))
        return True

    def _start_socket(self, sock, port):
        """Opens a socket connection to the given port

        sock -- the socket to perform a connection with
        port -- the port number to connect to
        """
        socket_error = None
        try:
            sock.connect((self._ip_address, port))
        except socket.error as e:
            socket_error = e

        result_code = self._get_result_code(socket_error.errno)
        return result_code

    def _check_sockets(self):
        sockets = [s.sock for s in self._in_progress.values()]
        _, ready, _ = select.select([], sockets, [], self._timeout)
        for sock in ready:
            socket_data = self._get_socket_data(sock.fileno())
            error_code = socket_data.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            result_code = self._get_result_code(error_code)
            if result_code == ScanResultCode.ERROR:
                self._finish_socket(socket_data, None)
                self._increment_retry(socket_data)
            else:
                self._finish_socket(socket_data, result_code)

        self._handle_timeouts()

    def _handle_timeouts(self):
        """Process for handling timeouts"""
        for socket_data in self._in_progress.values():
            if self._is_past_timeout(socket_data.start_time):
                if self._increment_retry(socket_data):
                    self._port_queue.append(socket_data.port)
                    self._finish_socket(socket_data, None)
                else:
                    self._finish_socket(socket_data, ScanResultCode.NO_ANSWER)

    def _get_result_code(self, error_code):
        if error_code == errno.EISCONN or error_code == 0:
            return ScanResultCode.OPEN
        if error_code == errno.ECONNREFUSED:
            return ScanResultCode.REFUSED
        if error_code == errno.EINPROGRESS or error_code == errno.EALREADY:
            return ScanResultCode.IN_PROGRESS
        if error_code == errno.ETIMEDOUT:
            return ScanResultCode.NO_ANSWER
        print 'Unknown error ' + str(error_code)
        return ScanResultCode.ERROR

    def _is_past_timeout(self, start_time):
        return (time.time() - start_time) >= self._timeout

    def _increment_retry(self, socket_data):
        key = socket_data.sock.fileno()
        retries = self._retries.get(key, 0)
        retries += 1
        self._retries[key] = retries
        return retries <= self._num_retries

    def _add_in_progress(self, socket_data):
        self._in_progress[socket_data.sock.fileno()] = socket_data

    def _get_socket_data(self, fd):
        return self._in_progress[fd]

    def _finish_socket(self, socket_data, result_code):
        key = socket_data.sock.fileno()
        socket_data = self._in_progress[key]
        del self._in_progress[key]
        if result_code:
            self._results.append(ResultData(socket_data.ip_address, socket_data.port, result_code))
        socket_data.sock.close()


def print_results(results):
    """Prints any open ports and reports the number of closed or filtered ports"""
    closed = 0
    filtered = 0
    for result in results:
        if result.result_code == ScanResultCode.REFUSED:
            closed += 1
        elif result.result_code == ScanResultCode.NO_ANSWER:
            filtered += 1

        print "{}:{} {}".format(result.ip_address, result.port, ScanResultCode.MESSAGE[result.result_code])

    if closed > 0:
        print '{} closed ports not shown'.format(closed)
    if filtered > 0:
        print '{} filtered ports not shown'.format(filtered)


if __name__ == '__main__':
    print 'Starting efficient port scanner'

    parser = argparse.ArgumentParser(description="Simple TCP port scanner that uses connect() calls to scan open"
                                          "ports.  All open ports will be printed out.")
    parser.add_argument("host", help="Host to be scanned.  Can be an address or a hostname.")
    parser.add_argument("--start-port", "-s", help="Start port", default=1)
    parser.add_argument("--end-port", "-e", help="End port", default=1024)
    parser.add_argument("--timeout", "-t", help="Timeout", default=PortScanner.DEFAULT_TIMEOUT)
    parser.add_argument("--num-retries", "-r", help="Number of times to attempt a port that doesn't answer",
                        default=PortScanner.DEFAULT_RETRIES)

    args = parser.parse_args()

    ip_address = socket.gethostbyname(args.host)

    if int(args.start_port) > int(args.end_port):
        print 'Start port must be less than or equal to end port'
        sys.exit(1)

    print 'Scanning {} on ports {}-{} with timeout {}'.format(ip_address, args.start_port, args.end_port, args.timeout,
                                                              args.num_retries)

    start_time = time.time()
    scanner = PortScanner(ip_address, start_port=int(args.start_port), end_port=int(args.end_port),
                          timeout=float(args.timeout), num_retries=int(args.num_retries))
    results = scanner.scan_ports()

    print 'Time to scan ports: ' + str("%.3f" % (time.time() - start_time))
    print_results(results)
