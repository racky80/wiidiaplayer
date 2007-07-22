class Titlebar {
	static public var __CLASS__:String = "Titlebar";
	private var oLogger:LuminicBox.Log.Logger;
	
	private var titleField:TextField;
	private var timeField:TextField;
	private var fpsField:TextField;

	private var titlebar_mc:MovieClip;
	private var visibilityTimer:Number;
	private var targetalpha:Number;
	private var openfileselector:Function;
	private var pausefunction:Function;
	private var timeproviderfunction:Function;
	private var fpsproviderfunction:Function;
	private var fileselector_btn:WiiButton;
	private var pause_btn:WiiButton;
	private var forceshow:Boolean = false
	private var forcehide:Boolean = false
	

	public function Titlebar(openfileselector:Function, pausefunction:Function, timeproviderfunction:Function, fpsproviderfunction:Function) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		targetalpha = 0;
		this.openfileselector=openfileselector
		this.pausefunction=pausefunction
		this.timeproviderfunction = timeproviderfunction
		this.fpsproviderfunction = fpsproviderfunction
	}
	
	public function draw(mc:MovieClip) {
		mc.createEmptyMovieClip("titlebar", mc.getNextHighestDepth())
		titlebar_mc = mc["titlebar"];

		titlebar_mc.beginGradientFill("linear", [0x7f7f7f, 0x7f7f7f],[100,0],[0,0xff], {matrixType:"box", x: 0, y:0 , w:Config.TITLEBAR_TOP_WIDTH, h:Config.TITLEBAR_TOP_HEIGHT, r:.5*Math.PI});
		titlebar_mc.moveTo(Config.TITLEBAR_TOP_X,Config.TITLEBAR_TOP_Y);
		titlebar_mc.lineTo(Config.TITLEBAR_TOP_X+Config.TITLEBAR_TOP_WIDTH,Config.TITLEBAR_TOP_Y);
		titlebar_mc.lineTo(Config.TITLEBAR_TOP_X+Config.TITLEBAR_TOP_WIDTH,Config.TITLEBAR_TOP_Y+Config.TITLEBAR_TOP_HEIGHT);
		titlebar_mc.lineTo(Config.TITLEBAR_TOP_X, Config.TITLEBAR_TOP_Y+Config.TITLEBAR_TOP_HEIGHT);
		titlebar_mc.endFill()
		
		titlebar_mc.createTextField("mytext",titlebar_mc.getNextHighestDepth(),Config.TITLEBAR_TITLE_X,Config.TITLEBAR_TITLE_Y, Config.TITLEBAR_TITLE_WIDTH, Config.TITLEBAR_TITLE_HEIGHT)
		this.titleField = titlebar_mc["mytext"];
		var tfmt:TextFormat = new TextFormat("defaultfont");
		tfmt.size=Config.TITLEBAR_FONTSIZE;
		tfmt.color=Config.TITLEBAR_FONTCOLOR;
		this.titleField.setNewTextFormat(tfmt)
		this.titleField.embedFonts=true;
		this.titleField.text="no title...";

		titlebar_mc.createTextField("mytime",titlebar_mc.getNextHighestDepth(),Config.TITLEBAR_TIME_X,Config.TITLEBAR_TIME_Y, Config.TITLEBAR_TIME_WIDTH, Config.TITLEBAR_TIME_HEIGHT)
		this.timeField = titlebar_mc["mytime"];
		this.timeField.setNewTextFormat(tfmt)
		this.timeField.embedFonts=true;

		titlebar_mc.createTextField("myfps",titlebar_mc.getNextHighestDepth(),Config.TITLEBAR_FPS_X,Config.TITLEBAR_FPS_Y, Config.TITLEBAR_FPS_WIDTH, Config.TITLEBAR_FPS_HEIGHT)
		this.fpsField = titlebar_mc["myfps"];
		this.fpsField.setNewTextFormat(tfmt)
		this.fpsField.embedFonts=true;

		titlebar_mc._alpha = 0;
		
		var self:Titlebar = this;
		titlebar_mc.onMouseMove = function () {self.mouseMoved()}
		titlebar_mc.onEnterFrame = function () {self.enterFrame()};

		fileselector_btn = new WiiButton("[ ]", Config.TITLEBAR_FILESELECTOR_BUTTON_WIDTH, Config.TITLEBAR_FILESELECTOR_BUTTON_HEIGHT);
		fileselector_btn.draw(titlebar_mc, true)
		fileselector_btn.setPosition(Config.TITLEBAR_FILESELECTOR_X,Config.TITLEBAR_FILESELECTOR_Y)
		fileselector_btn.setClickHandler(this.openfileselector)
		
		pause_btn = new WiiButton("||", Config.TITLEBAR_FILESELECTOR_BUTTON_WIDTH, Config.TITLEBAR_FILESELECTOR_BUTTON_HEIGHT);
		pause_btn.draw(titlebar_mc, true)
		pause_btn.setPosition(Config.TITLEBAR_PAUSE_X,Config.TITLEBAR_PAUSE_Y)
		pause_btn.setClickHandler(pausefunction)
		
		this.oLogger.debug("done drawing titlebar")
	}
	
	private function enterFrame() {
		var diff:Number = Math.min(Math.max(targetalpha-titlebar_mc._alpha, -Config.TITLEBAR_DISAPPEAR_SPEED), Config.TITLEBAR_APPEAR_SPEED);
		titlebar_mc._alpha += diff;
		if (titlebar_mc._alpha > 0) {
			titlebar_mc._visible = true;
			var oTime:Object = timeproviderfunction();
			setTime(oTime["status"], oTime["timeseconds"], oTime["seekoffset"], oTime["serversiderenderpos"], oTime["serversiderenderpct"])
			setFPS(fpsproviderfunction())
		} else {
			titlebar_mc._visible = false;
		}
	}
	
	private function mouseMoved() {
		var x:Number = titlebar_mc._parent._xmouse
		var y:Number = titlebar_mc._parent._ymouse
		
		if (x > Config.TITLEBAR_TOP_X && x < Config.TITLEBAR_TOP_X+Config.TITLEBAR_TOP_WIDTH &&
			y > Config.TITLEBAR_TOP_Y && y < Config.TITLEBAR_TOP_Y+Config.TITLEBAR_TOP_HEIGHT )	 {
			this.showMe();
		}
	}
	
	private function resetTimer() {
		var self:Titlebar = this;
		if (this.visibilityTimer) {
			clearInterval(this.visibilityTimer)
		}
		
		this.visibilityTimer = setInterval(function() {self.hideMe()}, Config.TITLEBAR_TIMEOUT)
	}
	
	private function showMe() {
		if (forcehide){
			return
		}
		this.resetTimer()
		this.targetalpha=Config.TITLEBAR_MAX_ALPHA;
	}
	
	private function hideMe() {
		if (forceshow){
			return
		}
		this.targetalpha=0;
	}
	
	public function forceShowMe(show:Boolean) {
		showMe()
		forceshow = show;
		oLogger.info("forceshow="+forceshow);
	}
	
	public function forceHideMe(hide:Boolean) {
		if (hide) {
			hideMe()
		}
		forcehide = hide;
		oLogger.info("forcehide="+forcehide);
	}
	
	public function setTitle(title:String) {
		this.titleField.text=title
		this.showMe();
	}
	
	public function setTime(status:Number, timeseconds:Number, seekoffset:Number, serversiderenderpos:Number, serversiderenderpct:Number) {
		switch (status) {
			case Wiidiaplayer.TIME_STATUS_STOP:
				this.timeField.text = "--:--"
			break;
			case Wiidiaplayer.TIME_STATUS_PAUSE:
				if ((new Date()).getMilliseconds() < 500) {
					this.timeField.text = ""
				} else {
					this.timeField.text = Util.formatAsTime(timeseconds)
				}
			break;
			case Wiidiaplayer.TIME_STATUS_PLAY:
				this.timeField.text = Util.formatAsTime(timeseconds)
			break;
			case Wiidiaplayer.TIME_STATUS_SEEK:
				showMe();
				this.timeField.text = Util.formatAsTime(timeseconds)+" "+(seekoffset>0?"+":"-")+Util.formatAsTime(Math.abs(seekoffset))
				if (serversiderenderpct !== undefined)
				this.timeField.text += "("+(Math.round(serversiderenderpct*1000)/10)+"%)"
			break;
		}
	}
	
	public function setFPS(fps:Number) {
		this.fpsField.text = "fps: "+Math.round(fps*10)/10;
	}
}