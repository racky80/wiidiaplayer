class VideoScreen {
	static public var __CLASS__:String = "VideoScreen";
	
	private var oLogger:LuminicBox.Log.Logger;
	
	private var videoDisplay:MovieClip;
	private var video:Video;
	private var nc:NetConnection;
	private var ns:NetStream;
	private var flushingBuffer:Boolean;
	private var streamendcallback:Function
	private var seekoffset:Number
	private var paused:Boolean
	private var stopped:Boolean
	private var medialength:Number
	private var mediaavailable:Number

	public function VideoScreen(streamendcallback:Function) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		this.streamendcallback = streamendcallback
		stopped=true
	}
	
	public function draw(mc:MovieClip) {
		var self:VideoScreen = this
		mc.attachMovie("VideoDisplay", "VideoDisplay", mc.getNextHighestDepth());
		this.videoDisplay = mc["VideoDisplay"]
		this.video = this.videoDisplay["vid"]
		this.nc = new NetConnection();
		this.nc.connect(Config.RTMP_SERVER_URL);
		ns = new NetStream(nc);
		ns.onStatus = function(infoObject:Object) {self.onStatus(infoObject)}
		this.video.attachVideo(this.ns);
		this.oLogger.info(mc)
		
	}
	
	public function playTest() {
		this.play(Config.RTMP_TESTFLV);
	}
	
	public function play(file:String) {
		this.oLogger.info("playing "+file)
		this.ns.play(file);
	}
	
	public function pause(pausemode:Boolean) {
		if (pausemode) {
			paused=pausemode
		} else {
			paused=!paused
		}
		this.oLogger.info("pause")
		ns.pause(paused);
	}
	
	public function seekprogress(timediff:Number) {
		seekoffset = timediff
	}
	
	public function seek(timediff:Number) {
		this.oLogger.info("seek "+timediff)
		seekoffset = timediff
		ns.seek(ns.time+timediff);
	}
	
	public function getStatus():Object {
		var result:Object = {
			medialength: medialength,
			mediaavailable: mediaavailable,
			timeseconds: ns.time
		}
		if (seekoffset !== undefined) {
			result["status"] = Wiidiaplayer.TIME_STATUS_SEEK
			result["seekoffset"] = seekoffset
		} else if (stopped) {
			result["status"] = Wiidiaplayer.TIME_STATUS_STOP
		} else if (paused) {
			result["status"] = Wiidiaplayer.TIME_STATUS_PAUSE
		} else {
			result["status"] = Wiidiaplayer.TIME_STATUS_PLAY
		}
		return result;
	}
	
	public function getCurrentFPS():Number {
		return ns.currentFps;
	}
	
	public function onStatus(infoObject:Object) {
		switch (infoObject["code"]) {
			case "NetStream.Play.Start":
				flushingBuffer = false
				seekoffset = undefined
				paused = false
				stopped = false
				medialength = undefined
				mediaavailable = undefined
			break;
			case "NetStream.Buffer.Flush":
				flushingBuffer = true
			break;
			case "NetStream.Error":
				// we'll just pretend nothing happened and play the next file
				stopped = true
				this.streamendcallback()
			case "NetStream.Buffer.Empty":
				if (flushingBuffer) {
					stopped = true
					this.streamendcallback()
				}
			break;
			case "Server.Media.Info":
				medialength = infoObject["totallength"]
				mediaavailable = infoObject["availablelength"]
			break;
			default:
				oLogger.info("onStatus received:")
				oLogger.info(infoObject)
		}
	}
}