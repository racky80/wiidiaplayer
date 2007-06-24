class Titlebar {
	static public var __CLASS__:String = "Titlebar";
	private var oLogger:LuminicBox.Log.Logger;
	
	private var textField:TextField;
	private var this_mc:MovieClip;
	private var visibilityTimer:Number;
	private var targetalpha:Number;
	

	public function Titlebar() {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		targetalpha = 0;
	}
	
	public function draw(mc:MovieClip) {
		mc.createEmptyMovieClip("titlebar", mc.getNextHighestDepth())
		this.this_mc = mc["titlebar"];

		this.this_mc.beginGradientFill("linear", [0x7f7f7f, 0x7f7f7f],[100,0],[0,0xff], {matrixType:"box", x: 0, y:0 , w:Stage.width, h:Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE, r:.5*Math.PI});
		this.this_mc.moveTo(0,0);
		this.this_mc.lineTo(Stage.width,0);
		this.this_mc.lineTo(Stage.width,Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE);
		this.this_mc.lineTo(0,Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE);
		this.this_mc.endFill()
		
		this.this_mc.createTextField("mytext",this_mc.getNextHighestDepth(),Config.TITLEBAR_PADDING,0, Stage.width, Config.TITLEBAR_PADDING*2+Config.TITLEBAR_FONTSIZE)
		this.textField = this.this_mc["mytext"];
		var tfmt:TextFormat = new TextFormat("defaultfont");
		tfmt.size=Config.TITLEBAR_FONTSIZE;
		tfmt.color=Config.TITLEBAR_FONTCOLOR;
		this.textField.setNewTextFormat(tfmt)
		this.textField.embedFonts=true;
		this.textField.text="no title...";
		this.this_mc._alpha = 0;
		var self:Titlebar = this;
		this.this_mc.onRollOver = function () {self.mouseIn()};
		this.this_mc.onRollOut = function () {self.mouseOut()};
		this.this_mc.onEnterFrame = function () {self.enterFrame()};
		this.oLogger.debug("done drawing titlebar")
	}
	
	private function enterFrame() {
		var diff:Number = Math.min(Math.max(targetalpha-this.this_mc._alpha, -Config.TITLEBAR_DISAPPEAR_SPEED), Config.TITLEBAR_APPEAR_SPEED);
		this.this_mc._alpha += diff;
	}
	
	private function mouseIn() {
		var self:Titlebar = this;
		this.showMe();
		this.this_mc.onMouseMove = function() {self.showMe()}
	}
	
	private function mouseOut() {
		var self:Titlebar = this;
		this.this_mc.onMouseMove = function() {}
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