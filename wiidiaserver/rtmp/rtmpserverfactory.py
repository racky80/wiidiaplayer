from twisted.internet import protocol
import rtmpprotocol

class RTMPServerFactory(protocol.ServerFactory):

	def __init__(self, mediapath):
		self.protocol = rtmpprotocol.RTMPProtocol
		self.mediapath = mediapath

	def buildProtocol(self, addr):
		p = self.protocol(self.mediapath)
		p.factory = self
		return p
		
