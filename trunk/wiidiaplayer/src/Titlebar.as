class Titlebar {
	static public var __CLASS__:String = "Titlebar";
	private var oLogger:LuminicBox.Log.Logger;
	
	private var textField:TextField;
	private var titlebar_mc:MovieClip;
	private var visibilityTimer:Number;
	private var targetalpha:Number;
	private var openfileselector:Function;
	private var pausefunction:Function;
	private var fileselector_btn:WiiButton;
	private var pause_btn:WiiButton;
	

	public function Titlebar(openfileselector:Function, pausefunction:Function) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		targetalpha = 0;
		this.openfileselector=openfileselector
		this.pausefunction=pausefunction
	}
	
	public function draw(mc:MovieClip) {
		mc.createEmptyMovieClip("titlebar", mc.getNextHighestDepth())
		titlebar_mc = mc["titlebar"];

		titlebar_mc.beginGradientFill("linear", [0x7f7f7f, 0x7f7f7f],[100,0],[0,0xff], {matrixType:"box", x: 0, y:0 , w:Stage.width, h:Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE, r:.5*Math.PI});
		titlebar_mc.moveTo(0,0);
		titlebar_mc.lineTo(Stage.width,0);
		titlebar_mc.lineTo(Stage.width,Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE);
		titlebar_mc.lineTo(0,Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE);
		titlebar_mc.endFill()
		
		titlebar_mc.createTextField("mytext",titlebar_mc.getNextHighestDepth(),Config.TITLEBAR_PADDING,0, Stage.width, Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE)
		this.textField = titlebar_mc["mytext"];
		var tfmt:TextFormat = new TextFormat("defaultfont");
		tfmt.size=Config.TITLEBAR_FONTSIZE;
		tfmt.color=Config.TITLEBAR_FONTCOLOR;
		this.textField.setNewTextFormat(tfmt)
		this.textField.embedFonts=true;
		this.textField.text="no title...";
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
	}
	
	private function mouseMoved() {
		if (titlebar_mc.hitTest(_root._xmouse, _root._ymouse, true)) {
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
		this.resetTimer()
		this.targetalpha=Config.TITLEBAR_MAX_ALPHA;
	}
	
	private function hideMe() {
		this.targetalpha=0;
	}
	
	
	public function setTitle(title:String) {
		this.textField.text=title
		this.showMe();
	}
}