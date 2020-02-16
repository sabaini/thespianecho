import sys
from datetime import timedelta

from thespian.actors import ActorSystem


if __name__ == "__main__":
    # We take the convention leaders address from the command line
    # Also, we tag this system with "Client"
    capabilities = {"Convention Address.IPv4": (sys.argv[1], 1900), "Client": True}
    actor_system = ActorSystem("multiprocTCPBase", capabilities)
    # We create an actor from the echo library with class EchoRequestor
    echo_app = actor_system.createActor("echo.EchoRequestor")
    # Send the echo actor a message: the number of echo requests it should perform
    actor_system.tell(echo_app, int(sys.argv[2]))
    # Now, send the echo payload, and wait max. 10s for an answer
    resp = actor_system.ask(echo_app, "hello world", timedelta(seconds=10))
    while resp:
        # If we get "echo_done" as an answer we break out
        if resp == "echo_done":
            break
        # Otherwise we'll retry to get a response
        print("unexpected message {}".format(resp))
        resp = actor_system.listen(timedelta(seconds=10))
