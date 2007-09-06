class Wiidiaplayer {
	
	static public var __CLASS__:String = "Wiidiaplayer";
	
	private var oLogger:LuminicBox.Log.Logger;
	
	private var root:MovieClip;
	private var titlebar:Titlebar;
	private var video:VideoScreen;
	private var fileSelector:FileSelector;
	private var dragger:Dragger;
	private var playlist:Playlist;
	
	private var s:Sound;
	
	
	static public var TIME_STATUS_STOP:Number=1;
	static public var TIME_STATUS_PAUSE:Number=2;
	static public var TIME_STATUS_PLAY:Number=3;
	static public var TIME_STATUS_SEEK:Number=4;
	
	function Wiidiaplayer(rootclip:MovieClip) {
		
		var self:Wiidiaplayer = this
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		var sound:Sound = new Sound()
		sound.setVolume(100)

		this.root=rootclip;
		
		video = new VideoScreen(function() {self.playlist.selectNext()} );
		video.draw(this.root);
		
		this.titlebar = new Titlebar(	function() {self.fileSelector.open(); self.titlebar.forceHideMe(true);},
										function() {self.playlist.show();},
										function() {self.video.pause()} ,
										function():Object {return self.getPlaybackStatus()},
										function():Number {return self.getCurrentFPS()},
										function() {self.playlist.selectNext()},
										function() {self.playlist.selectPrevious()}
										);
		this.titlebar.draw(this.root)
		
		this.playlist = new Playlist(function(playlistentry:PlaylistEntry) {
					var file:String = playlistentry.getFilename();
					self.oLogger.info("playing "+file);
					self.video.play(file);
					self.titlebar.setTitle(Util.basename(file))
				})
		this.playlist.draw(this.root);
		this.playlist.show(false);
		
		openFileSelector();
		
		this.dragger = new Dragger( function() {self.draggingStart()},
									function(dx:Number, dy:Number) {self.draggingEnded(dx, dy)},
									function(dx:Number, dy:Number) {self.draggingProgress(dx, dy)}
								);
		setInterval(function() {
				Util.sendFeedback(""+self.getCurrentFPS())
		}, 5000);
	}
	
	function draggingStart() {
		oLogger.info("dragging started")
		this.titlebar.forceShowMe(true);
		video.pause(true)
	}
	
	function draggingProgress(dx:Number, dy:Number) {
		video.seekprogress(getSeekFromDrag(dx))
	}
	
	function draggingEnded(dx:Number, dy:Number) {
		this.titlebar.forceShowMe(false);
		oLogger.info("dragging ended: "+dx+", "+dy )
		var status:Object = video.getStatus()
		if (status["status"] != Wiidiaplayer.TIME_STATUS_STOP)  {
			video.pause(false)
			video.seek(getSeekFromDrag(dx))
		}
	}
	
	function getSeekFromDrag(dx:Number):Number {
		var status:Object = video.getStatus()
		var medialength:Number = status["medialength"]
		if (medialength == undefined) {
			medialength = status["timeseconds"]*2;
		}
		if (dx > 0) {
			return (medialength -status["timeseconds"])*Math.min(1, Math.pow(dx,2)/Math.pow(Stage.width-2*Config.APPLICATION_DRAGGING_SCREENSIDES_SIZE,2));
		} else {
			return -(status["timeseconds"])*Math.min(1, Math.pow(dx,2)/Math.pow(Stage.width-2*Config.APPLICATION_DRAGGING_SCREENSIDES_SIZE,2));
		}
	}
	
	/**
	* Returns the time in seconds to be displayed on the status line
	**/
	function getPlaybackStatus():Object {
		return video.getStatus();
	}
	
	function getCurrentFPS():Number {
		return video.getCurrentFPS();
	}
	
	
	static function main(mc:MovieClip) {
		_root.app = new Wiidiaplayer(mc); // need to assign this variable somewhere, since else the flash 7 GC thinks the objects is out of scope and destroys it right away
	}
	
	
	function openFileSelector(opennew:Boolean) {
		var self:Wiidiaplayer = this
		if (!fileSelector || opennew) {
			fileSelector = new FileSelector(function(aFile:/*String*/Array) {
				self.closeFileSelector()
				if (aFile.length == 0) {
					return;
				}
				var aEntry:/*PlaylistEntry*/Array = new Array();
				for(var i:Number=0;i<aFile.length;i++) {
					self.oLogger.info("play: "+aFile[i]);
					aEntry.push(new PlaylistEntry(aFile[i]));
				}
				var nr:Number = self.playlist.addEntries(aEntry)
				self.playlist.selectNext(nr);
			})
			
			fileSelector.draw(root)
		}
		fileSelector.open();
		titlebar.forceHideMe(true);
	}
	
	function closeFileSelector(destroy:Boolean) {
		titlebar.forceHideMe(false);
		fileSelector.close()
		
		if (destroy) {
			fileSelector = undefined
		}
	}
}