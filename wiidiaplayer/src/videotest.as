class videotest{
	private var video:Video;
	private var nc:NetConnection;
	private var ns:NetStream;
	
	function videotest()       {
		_root.attachMovie("VideoDisplay", "VideoDisplay", _root.getNextHighestDepth());
		// Create a NetConnection object
		nc = new NetConnection();
		// Create a local streaming connection
		nc.connect(null);
		ns = new NetStream(nc);
		// Attach the NetStream video feed to the Video object
		_root["VideoDisplay"]["vid"].attachVideo(ns);
		// Begin playing the FLV file
		ns.play("test.flv");
	       }

	static function main(){
		var vt:videotest=new videotest();
	}
}
