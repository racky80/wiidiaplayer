class FileSelector {
	static public var __CLASS__:String = "FileSelector";
	private var oLogger:LuminicBox.Log.Logger;
	
	private var currentpath:String
	private var fileselector_mc:MovieClip

	public function FileSelector() {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		
		this.currentpath = ''
	}
	
	/**
	 * Note: the FileSelector will still be invisible when drawn, use the open method to show it	 */
	public function draw(mc:MovieClip) {
		mc.createEmptyMovieClip("fileselector", mc.getNextHighestDepth())
		fileselector_mc = mc["fileselector"];

		fileselector_mc.beginFill(0xcfcfdf);
		fileselector_mc.moveTo(Config.FILESELECTOR_X,Config.FILESELECTOR_Y);
		fileselector_mc.lineTo(Config.FILESELECTOR_X+Config.FILESELECTOR_WIDTH,Config.FILESELECTOR_Y);
		fileselector_mc.lineTo(Config.FILESELECTOR_X+Config.FILESELECTOR_WIDTH, Config.FILESELECTOR_Y+Config.FILESELECTOR_HEIGHT);
		fileselector_mc.lineTo(Config.FILESELECTOR_X, Config.FILESELECTOR_Y+Config.FILESELECTOR_HEIGHT);
		fileselector_mc.endFill()
		
		fileselector_mc._alpha = 80
		fileselector_mc._visible = false
	}
	
	public function open() {
		fileselector_mc._visible = true
	}
	
	private function retrieveAndShowDirContents() {
		
	}
}