class Playlist {
    static public var __CLASS__:String = "Playlist";
    private var oLogger:LuminicBox.Log.Logger;
    
    static public var PLAYLIST_MODE_SINGLE:Number = 1
    static public var PLAYLIST_MODE_REPEAT:Number = 2
    
    private var onSelectEntry:Function;
    private var playlist_mc:MovieClip
    private var playlist_list_mc:MovieClip
    private var aEntry:/*PlaylistEntry*/Array
    private var selectedIndex:Number
    private var shuffle_btn:WiiButton
    private var mode:Number

    public function Playlist(selectEntry:Function) {
        this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
        this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
        this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
        this.oLogger.info("__init__ "+__CLASS__);
        
        this.setMode(PLAYLIST_MODE_SINGLE)

        this.onSelectEntry=selectEntry
        reset();
    }
    
    public function draw(mc:MovieClip) {
    	var self:Playlist=this
        mc.createEmptyMovieClip("playlist", mc.getNextHighestDepth())
        playlist_mc = mc["playlist"];

        playlist_mc.beginFill(Config.PLAYLIST_BGCOLOR);
        playlist_mc.moveTo(Config.PLAYLIST_X,Config.PLAYLIST_Y);
        playlist_mc.lineTo(Config.PLAYLIST_X+Config.PLAYLIST_WIDTH,Config.PLAYLIST_Y);
        playlist_mc.lineTo(Config.PLAYLIST_X+Config.PLAYLIST_WIDTH,Config.PLAYLIST_Y+Config.PLAYLIST_HEIGHT);
        playlist_mc.lineTo(Config.PLAYLIST_X,Config.PLAYLIST_Y+Config.PLAYLIST_HEIGHT);
        playlist_mc.endFill()

        playlist_mc.createEmptyMovieClip("playlist_list", playlist_mc.getNextHighestDepth())
        playlist_list_mc = playlist_mc["playlist_list"];

        playlist_list_mc.beginFill(Config.PLAYLIST_LIST_BGCOLOR);
        playlist_list_mc.moveTo(0,0);
        playlist_list_mc.lineTo(Config.PLAYLIST_LIST_WIDTH,0);
        playlist_list_mc.lineTo(Config.PLAYLIST_LIST_WIDTH,Config.PLAYLIST_LIST_HEIGHT);
        playlist_list_mc.lineTo(0,Config.PLAYLIST_LIST_HEIGHT);
        playlist_list_mc.endFill()
        
        playlist_list_mc._x = 0;
        playlist_list_mc._y = Config.PLAYLIST_LIST_Y;

		shuffle_btn = new WiiButton("mix", Config.FILESELECTOR_NAVBUTTON_WIDTH, Config.FILESELECTOR_NAVBUTTON_HEIGHT)
		shuffle_btn.draw(playlist_mc, true)
		shuffle_btn.setPosition(Config.PLAYLIST_PADDING+Config.FILESELECTOR_NAVBUTTON_WIDTH*0.5, Config.FILESELECTOR_NAVBUTTON_HEIGHT/2+Config.PLAYLIST_PADDING)
		shuffle_btn.setClickHandler(function() {self.shuffle()})

        this.oLogger.info("done drawing "+__CLASS__)
    }
    
    public function setMode(mdoe:Number) {
    	this.mode=mode;
    }
    
    public function reset() {
    	aEntry = new Array();
    	selectedIndex = undefined
    }
    
    public function addEntries(aEntryToAdd:/*PlaylistEntry*/Array):Number{
    	var self:Playlist=this
    	var addedstart:Number = aEntry.length
    	aEntry=aEntry.concat(aEntryToAdd);
    	for(var i:Number=addedstart;i<aEntry.length;i++) {
    		aEntry[i].draw(playlist_list_mc);
    		aEntry[i].setVerticalPosition((i)*Config.PLAYLIST_ENTRYHEIGHT+(i+1)*Config.PLAYLIST_PADDING)
    		aEntry[i].onClick = function(nr:Number):Function{ return function():Boolean{return self.selectNext(nr)} }(i)
    	}
        this.oLogger.info(aEntry)
        return addedstart
    }
    
    private function selectEntry(entrynr:Number):Boolean {
    	if (entrynr >= aEntry.length) {
    		return false
    	}
    	if (selectedIndex != undefined) {
	    	aEntry[selectedIndex].activate(false)
    	}
   		onSelectEntry(aEntry[entrynr])
   		selectedIndex = entrynr
    	aEntry[selectedIndex].activate(true)
    	return true
    }
    
    /**
     * Shuffles the playlist
     */    public function shuffle() {
    	var mapper:Array = new Array();
    	for(var i:Number=0; i<aEntry.length;i++) {
	    	mapper.push({nr: i, sort: Math.random()})
    	}
    	mapper.sortOn("sort");
    	var aNewEntry:/*PlaylistEntry*/Array = new Array()
    	var newSelectedIndex:Number = undefined
    	for(var i:Number=0; i<mapper.length;i++) {
    		aNewEntry.push(aEntry[mapper[i].nr])
    		aNewEntry[i].setVerticalPosition((i)*Config.PLAYLIST_ENTRYHEIGHT+(i+1)*Config.PLAYLIST_PADDING)
    		if (selectedIndex == mapper[i].nr) {
		    	newSelectedIndex = i
    		}
    	}
    	aEntry = aNewEntry
    	selectedIndex = newSelectedIndex
    }
    
    public function selectNext(nr:Number):Boolean {
    	if (nr === undefined) {
    		if (selectedIndex === undefined) {
    			nr = 0
    		} else {
				nr = selectedIndex+1;
    		}
			if (nr >= aEntry.length) {
	    		switch (mode) {
	    			case Playlist.PLAYLIST_MODE_SINGLE:
    					nr = undefined
    				break;
	    			case Playlist.PLAYLIST_MODE_REPEAT:
	    				nr = 0
    				break;
    			default:
    				nr = undefined // should never happen
	    		}
	    	}
    	}
    	if (nr === undefined) {
    		return false
    	}
   		return selectEntry(nr)
    }
    
    public function selectPrevious():Boolean {
    	var nr:Number;
    	if (nr === undefined) {
    		if (selectedIndex === undefined) {
    			nr = aEntry.length-1
    		} else {
				nr = selectedIndex-1;
    		}
			if (nr < 0) {
	    		switch (mode) {
	    			case Playlist.PLAYLIST_MODE_SINGLE:
    					nr = undefined
    				break;
	    			case Playlist.PLAYLIST_MODE_REPEAT:
	    				nr = aEntry.length-1
    				break;
    			default:
    				nr = undefined // should never happen
	    		}
	    	}
    	}
    	if (nr === undefined) {
    		return false
    	}
   		return selectEntry(nr)
   }
    
    public function show(show:Boolean) {
    	oLogger.info("Playlist show: "+show)
    	if (show === undefined) {
    		show = !playlist_mc._visible
    	}
    	oLogger.info("Playlist show: "+show)
    	playlist_mc._visible = show
    }
}