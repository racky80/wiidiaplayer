class Wiidiaplayer {
	static public var __CLASS__:String = "Wiidiaplayer";
	
	private var root:MovieClip;
	private var video:VideoScreen;
	private var fileSelector:FileSelector;
	private var oLogger:LuminicBox.Log.Logger;
	
	
	function Wiidiaplayer(rootclip:MovieClip) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);

		this.root=rootclip;
		
		video = new VideoScreen();
		video.draw(this.root);
	//	video.playTest();
	
		fileSelector = new FileSelector()
		fileSelector.draw(root)
		fileSelector.open();
		
//		var but:WiiButton = new WiiButton("hallo daar dit ", 200, 30);
//		but.draw(this.root);
//		but.setPosition(200,200);
	}
	
	
	static function main(mc:MovieClip) {
		_root.app = new Wiidiaplayer(mc); // need to assign this variable somewhere, since else the flash 7 GC thinks the objects is out of scope and destroys it right away
	}
}