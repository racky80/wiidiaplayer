class Wiidiaplayer {
	static public var __CLASS__:String = "Wiidiaplayer";
	private var oLogger:LuminicBox.Log.Logger;
	
	private var root:MovieClip;
	private var titlebar:Titlebar;
	private var video:VideoScreen;
	private var fileSelector:FileSelector;
	private var dragger:Dragger;
	
	
	function Wiidiaplayer(rootclip:MovieClip) {
		var self:Wiidiaplayer = this
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		var sound:Sound = new Sound()
		sound.setVolume(100)

		this.root=rootclip;
		
		video = new VideoScreen();
		video.draw(this.root);

		
		fileSelector = new FileSelector(function(file:String) {
			self.titlebar.forceHideMe(false);
			self.fileSelector.close()
			if (file == "") {
				return;
			}
			self.oLogger.info("playing "+file);
			self.video.play(file);
			self.titlebar.setTitle(Util.basename(file))
		})
		
		fileSelector.draw(root)
		fileSelector.open();


		this.titlebar = new Titlebar(function() {self.fileSelector.open(); self.titlebar.forceHideMe(true);}, function() {self.video.pause()} , function():Number {return self.getPlaybackTime()});
		this.titlebar.draw(this.root)
		titlebar.forceHideMe(true);
		
		this.dragger = new Dragger( function() {self.draggingStart()},
									function(dx:Number, dy:Number) {self.draggingEnded(dx, dy)}
								);
	}
	
	function draggingStart() {
		oLogger.info("dragging started")
		this.titlebar.forceShowMe(true);
	}
	
	function draggingEnded(dx:Number, dy:Number) {
		this.titlebar.forceShowMe(false);
		oLogger.info("dragging ended: "+dx+", "+dy )
		video.seek(getSeekFromDrag(dx))
	}
	
	function getSeekFromDrag(dx:Number):Number {
		return Config.APPLICATION_DRAGGING_SCREENWIDTH_TIME_SECONDS*dx/Stage.width;
	}
	
	/**
	* Returns the time in seconds to be displayed on the status line
	**/
	function getPlaybackTime():Number {
		var dragx:Number = dragger.getDragDistance()["x"]
		return Math.max(video.getTime() + getSeekFromDrag(dragx),0);
	}
	
	
	static function main(mc:MovieClip) {
		_root.app = new Wiidiaplayer(mc); // need to assign this variable somewhere, since else the flash 7 GC thinks the objects is out of scope and destroys it right away
	}
}