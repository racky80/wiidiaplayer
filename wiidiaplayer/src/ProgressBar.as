class ProgressBar {
	static public var __CLASS__:String = "ProgressBar";
	
	private var oLogger:LuminicBox.Log.Logger;
	
	private var progressBar:MovieClip;
	private var bar:MovieClip;
	private var barfill:MovieClip;
	private var pointertop:MovieClip;
	private var pointerbottom:MovieClip;
	private var statusprovider:Function
	private var interval:Number;
	private var updatecounter:Number;

	public function ProgressBar(statusprovider:Function) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		this.statusprovider = statusprovider
	}
	
	public function draw(mc:MovieClip) {
		var self:ProgressBar = this
		mc.createEmptyMovieClip("progressbar", mc.getNextHighestDepth())
		this.progressBar = mc["progressbar"]
		

		this.progressBar.createEmptyMovieClip("bar", this.progressBar.getNextHighestDepth())
		this.bar = this.progressBar["bar"]
		this.bar.beginFill(Config.PROGRESSBAR_BAR_COLOR)
		this.bar.moveTo(0,0)
		this.bar.lineTo(Config.PROGRESSBAR_BAR_WIDTH,0)
		this.bar.lineTo(Config.PROGRESSBAR_BAR_WIDTH,Config.PROGRESSBAR_BAR_HEIGHT)
		this.bar.lineTo(0,Config.PROGRESSBAR_BAR_HEIGHT)
		this.bar.endFill();
		
		this.bar._x = Config.PROGRESSBAR_PADDING;
		this.bar._y = Config.PROGRESSBAR_Y;

		this.progressBar.createEmptyMovieClip("barfill", this.progressBar.getNextHighestDepth())
		this.barfill = this.progressBar["barfill"]
		this.barfill.beginFill(Config.PROGRESSBAR_BAR_AVAILABLE_COLOR)
		this.barfill.moveTo(0,0)
		this.barfill.lineTo(Config.PROGRESSBAR_BAR_WIDTH,0)
		this.barfill.lineTo(Config.PROGRESSBAR_BAR_WIDTH,Config.PROGRESSBAR_BAR_HEIGHT)
		this.barfill.lineTo(0,Config.PROGRESSBAR_BAR_HEIGHT)
		this.barfill.endFill();
		this.barfill._x = Config.PROGRESSBAR_PADDING;
		this.barfill._y = Config.PROGRESSBAR_Y;


		this.progressBar.createEmptyMovieClip("pointertop", this.progressBar.getNextHighestDepth())
		this.pointertop = this.progressBar["pointertop"]
		this.pointertop.lineStyle(1,0xFFFFFF)
		this.pointertop.beginFill(0x000000)
		this.pointertop.moveTo(0,0)
		this.pointertop.lineTo(6,-10)
		this.pointertop.lineTo(-6,-10)
		this.pointertop.endFill();

		this.progressBar.createEmptyMovieClip("pointerbottom", this.progressBar.getNextHighestDepth())
		this.pointerbottom = this.progressBar["pointerbottom"]
		this.pointerbottom.lineStyle(1,0xFFFFFF)
		this.pointerbottom.beginFill(0x000000)
		this.pointerbottom.moveTo(0,0)
		this.pointerbottom.lineTo(6,10)
		this.pointerbottom.lineTo(-6,10)
		this.pointerbottom.endFill();

		this.pointertop._y = Config.PROGRESSBAR_Y+Config.PROGRESSBAR_BAR_HEIGHT/2;
		this.pointerbottom._y = Config.PROGRESSBAR_Y+Config.PROGRESSBAR_BAR_HEIGHT/2;
		
	}
	
	public function update() {
		var status:Object = this.statusprovider()
		if (status["status"] == Wiidiaplayer.TIME_STATUS_STOP) {
			return;
		}
		
		var seekprt:Number = ((status["seekoffset"]?status["seekoffset"]:0)+status["timeseconds"])/status["medialength"]
		var playprt:Number = status["timeseconds"]/status["medialength"]
		var availprt:Number = status["mediaavailable"]/status["medialength"]

		this.barfill._xscale=100*availprt
		
		this.pointertop._x = Config.PROGRESSBAR_PADDING+Config.PROGRESSBAR_BAR_WIDTH*seekprt
		this.pointerbottom._x = Config.PROGRESSBAR_PADDING+Config.PROGRESSBAR_BAR_WIDTH*playprt
		
		oLogger.info("Drawn statusbar");
	}
}