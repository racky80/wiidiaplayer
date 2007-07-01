from twisted.internet import protocol
import rtmpprotocol

class RTMPServerFactory(protocol.ServerFactory):
    protocol = rtmpprotocol.RTMPProtocol
