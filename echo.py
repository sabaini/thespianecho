import datetime
import logging
import logging.handlers

from thespian.actors import ActorTypeDispatcher, requireCapability

# Set up some logging to see what is going on
log = logging.getLogger("Echologger")
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address="/dev/log")
log.addHandler(handler)


class Ping:
    """A simple object that just carries a payload"""

    def __init__(self, payload):
        self.payload = payload


class Pong(Ping):
    """Same as the ping class. 

    We subclass it so we can distinguish it by type, but it's really the same thing
    """
    pass


@requireCapability("Server")
class EchoServer(ActorTypeDispatcher):
    """The echo server actor

    It will receive ping messages, log them, and reply back to the sender with 
    a pong message

    Specifies a system tagged with the "Server" capability as a requirement. 
    This will cause the linked actor systems to instantiate it on the server
    actor system
    """

    def receiveMsg_Ping(self, ping_request, sender):
        log.debug("Got {}, ponging back at {}".format(ping_request, sender))
        self.send(sender, Pong(ping_request.payload))


@requireCapability("Client")
class EchoRequestor(ActorTypeDispatcher):
    """The echo client actor
    
    It specifies an actor system tagged with the "Client" capability. The
    client module is tagged with Client: True, so this actor will get
    get started on the client actor system
    """

    echo_server = None  # hold an echo server instance

    def __init__(self):
        # Initialise counters and timer, and calls the superclass constructor
        self.pings_to_send = 0
        self.pongs_to_receive = 0
        self.time = None
        super().__init__()

    def receiveMsg_int(self, count, _client):
        """Add integer as a count of pings to send
        
        If this actor receives an integer, it'll interpret it as 
        a count of pings, and add it to the pings to send counter
        """
        self.pings_to_send += count

    def receiveMsg_str(self, payload, client):
        """Receive a payload and start pinging

        If this actor receives a str message, it'll interpret it as a paylod 
        to ping with, and start pinging the number of times
        """
        # First we save the client, we will need it later to notify once we're done
        self.client = client
        # Then, instantiate an echo server. As the EchoServer class has a requirement
        # "Server" it'll get started on the actor system tagged with the "Server" capability
        self.echo_server = self.createActor(EchoServer)
        # Then start to send out ping messages, and save the start time
        ping = Ping(payload)
        log.debug(
            "Sending, srv: {}; message: {}; count: {}".format(
                self.echo_server, ping, self.pings_to_send
            )
        )
        self.time = datetime.datetime.now()
        for _ in range(1, self.pings_to_send):
            # Fire out pings_to_send pings to the server
            self.send(self.echo_server, ping)
        # Update counters
        self.pongs_to_receive += self.pings_to_send
        self.pings_to_send = 0

    def receiveMsg_Pong(self, _pong, _server):
        # Receive answers back from the echo server actor
        # We decrease the counter until it's zero
        self.pongs_to_receive -= 1
        if self.pongs_to_receive <= 1:
            log.info(
                "Got all messages, timedelta: {}".format(
                    datetime.datetime.now() - self.time
                )
            )
            # We're done, send a message to the client saying so
            log.info("Sending end request to {}".format(self.client))
            self.send(self.client, "echo_done")
