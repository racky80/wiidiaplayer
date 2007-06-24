class VideoScreen {
	static public var __CLASS__:String = "VideoScreen";
	
	private var oLogger:LuminicBox.Log.Logger;
	
	private var titlebar:Titlebar;
	private var videoDisplay:MovieClip;
	private var video:Video;
	private var nc:NetConnection;
	private var ns:NetStream;

	public function VideoScreen() {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		this.titlebar = new Titlebar();
	}
	
	public function draw(mc:MovieClip) {
		mc.attachMovie("VideoDisplay", "VideoDisplay", mc.getNextHighestDepth());
		this.videoDisplay = mc["VideoDisplay"]
		this.video = this.videoDisplay["vid"]
		this.nc = new NetConnection();
		this.nc.connect(Config.RTMP_SERVER_URL);
		ns = new NetStream(nc);
		this.video.attachVideo(this.ns);
		this.titlebar.draw(this.videoDisplay)
		this.oLogger.info(mc)
	}
	
	public function playTest() {
		this.play(Config.RTMP_TESTFLV);
	}
	
	public function play(file:String) {
		this.titlebar.setTitle(Util.basename(file))
		this.oLogger.info("playing "+file)
		this.ns.play(file);
	}
}