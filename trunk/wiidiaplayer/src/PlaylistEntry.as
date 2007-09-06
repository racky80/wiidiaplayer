class PlaylistEntry {
    static public var __CLASS__:String = "PlaylistEntry";
    static private var count:Number=0;
    private var oLogger:LuminicBox.Log.Logger;
    
    private var playlistentry_mc:MovieClip
    private var filename:String
    private var thiscount:Number
    private var titleField:TextField
    public var onClick:Function

    public function PlaylistEntry(filename:String) {
        this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
        this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
        this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
        this.filename = filename
        
        thiscount = PlaylistEntry.count++
    }
    
    public function draw(mc:MovieClip) {
    	var self:PlaylistEntry = this
		mc.createEmptyMovieClip("playlistentry_"+thiscount,mc.getNextHighestDepth());
		playlistentry_mc = mc["playlistentry_"+thiscount];
		playlistentry_mc.onPress = function() {if (self.onClick) {self.onClick()}}
		
        playlistentry_mc.createTextField("mytext",playlistentry_mc.getNextHighestDepth(),0,0, Config.PLAYLIST_WIDTH-2*Config.PLAYLIST_PADDING, Config.PLAYLIST_ENTRYHEIGHT)
        this.titleField = playlistentry_mc["mytext"];
        var tfmt:TextFormat = new TextFormat("defaultfont");
        tfmt.size=Config.PLAYLISTENTRY_FONTSIZE;
        tfmt.color=Config.PLAYLISTENTRY_FONTCOLOR_INACTIVE;
        this.titleField.setNewTextFormat(tfmt)
        this.titleField.embedFonts=true;
        this.titleField.text=Util.basename(filename);

    }

	public function setVerticalPosition(y:Number) {
		playlistentry_mc._x = Config.PLAYLIST_PADDING;
		playlistentry_mc._y = y;
	}
	
	public function getFilename():String {
		return filename
	}
	
	public function activate(activate:Boolean) {
        var tfmt:TextFormat = new TextFormat();
        if (activate) {
	        tfmt.color=Config.PLAYLISTENTRY_FONTCOLOR_ACTIVE;
        } else {
	        tfmt.color=Config.PLAYLISTENTRY_FONTCOLOR_INACTIVE;
        }
        this.titleField.setTextFormat(tfmt)
	}
	
}