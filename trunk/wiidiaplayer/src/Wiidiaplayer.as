﻿class Wiidiaplayer {
	static public var __CLASS__:String = "Wiidiaplayer";
	
	private var root:MovieClip;
	private var titlebar:Titlebar;
	private var video:VideoScreen;
	private var fileSelector:FileSelector;
	private var oLogger:LuminicBox.Log.Logger;
	
	
	function Wiidiaplayer(rootclip:MovieClip) {
		var self:Wiidiaplayer = this
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		var sound:Sound = new Sound()
		this.oLogger.info("volume "+sound.getVolume());

		this.root=rootclip;
		
		video = new VideoScreen();
		video.draw(this.root);

		
		fileSelector = new FileSelector(function(file:String) {
			self.oLogger.info("playing "+file);
			self.video.play(file);
			self.fileSelector.close()
			self.titlebar.setTitle(Util.basename(file))
		})
		
		fileSelector.draw(root)
		fileSelector.open();


		this.titlebar = new Titlebar(function() {self.fileSelector.open()}, function() {self.video.pause()} );
		this.titlebar.draw(this.root)
		
	}
	
	
	static function main(mc:MovieClip) {
		_root.app = new Wiidiaplayer(mc); // need to assign this variable somewhere, since else the flash 7 GC thinks the objects is out of scope and destroys it right away
	}
}