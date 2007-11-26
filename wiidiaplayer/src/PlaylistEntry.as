class PlaylistEntry extends WiiButton {
    static public var __CLASS__:String = "PlaylistEntry";
    static private var count:Number=0;
    private var oLogger:LuminicBox.Log.Logger;
    
    private var playlistentry_mc:MovieClip

    public function PlaylistEntry(filename:String) {
    	super(filename, Config.ITEMSELECTOR_FILEBUTTON_WIDTH, Config.ITEMSELECTOR_FILEBUTTON_HEIGHT)
        this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
        this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
        this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
    }
	
	public function getFilename():String {
		return text
	}
	
}