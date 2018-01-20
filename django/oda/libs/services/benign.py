import dns
import logging

import socket

logger = logging.getLogger(__name__)


def lookup_benign(binary):
    # lookup in national software reference library
    benign = False
    try:
        sock = socket.create_connection(('nsrl.kyr.us', 9120), timeout=0.5)
        sock.send('Version: 2.0\n')
        ack_ver = sock.recv(4096)
        sock.send('query %s\n' % binary.md5())
        ack_sum = sock.recv(4096)
        sock.send('BYE\n')
        if ack_ver.startswith('OK') and ack_sum.startswith('OK 1'):
            benign = True
        sock.close()
    except Exception:
        pass
