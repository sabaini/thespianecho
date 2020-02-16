import logging.handlers
import socket

from thespian.actors import ActorSystem


def get_my_ip():
    """Return the ipaddress of the local host"""
    return socket.gethostbyname(socket.gethostname())


if __name__ == "__main__":
    # Setting up some logging
    log = logging.getLogger("Echologger")
    log.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    log.addHandler(handler)

    # Setup this system as the convention leader, and give it a capability "Server"
    # Note by default actor systems use port 1900, so we'll set this here too
    capabilities = {"Convention Address.IPv4": (get_my_ip(), 1900), "Server": True}
    ActorSystem("multiprocTCPBase", capabilities)
