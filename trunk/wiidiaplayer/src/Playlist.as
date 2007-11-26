class Playlist extends ItemSelector {
    static public var __CLASS__:String = "Playlist";
    
    static public var PLAYLIST_MODE_SINGLE:Number = 1
    static public var PLAYLIST_MODE_REPEAT:Number = 2
    
    private var mode:Number
    private var onSelectEntry:Function
    private var selectedIndex:Number
    private var closeMe:Function

	public function Playlist(onSelectEntry:Function, closeMe:Function) {
		this.onSelectEntry = onSelectEntry;
		this.closeMe = closeMe;
		var self:Playlist = this;
		super(function(nr:Number) {if (nr != []) { self.selectNext(nr)}; self.closeMe()})
        this.setMode(PLAYLIST_MODE_SINGLE)
        reset();
	}

	/**
	 * Note: the Playlist will still be invisible when drawn, use the open method to show it
	 */
	public function draw(mc:MovieClip) {
		super.draw(mc)
		var self:Playlist = this
		up_btn.setEnabled(false)
		add_btn.setClickHandler(function() {self.shuffle()})
		
	}
	
	public function open() {
		drawButtons()
		super.open();
	}
	
	private function setCorrectCallbacksToButtons() {
		var self:Playlist = this
		var i:Number;
		for(i=0;i<itembuttons.length;i++){
			itembuttons[i].setClickHandler(function(nr:Number):Function{ return function():Boolean{return self.callback(nr)} }(i))
		}
	}
	
	private function drawButtons(){
		super.drawButtons();
		itembuttons[selectedIndex].activate(true)
		this.setTitle("Playlist (page "+(pagenr+1)+")")
	}
    
    public function setMode(mode:Number) {
    	this.mode=mode;
    }
    
    public function reset() {
    	itembuttons = new Array();
    	selectedIndex = undefined
    	
    }
    
    public function addEntries(itembuttonsToAdd:/*PlaylistEntry*/Array):Number{
    	var self:Playlist=this
    	var addedstart:Number = itembuttons.length
    	itembuttons=itembuttons.concat(itembuttonsToAdd);
    	setCorrectCallbacksToButtons()
        return addedstart
    }
    
    private function selectEntry(entrynr:Number):Boolean {
    	if (entrynr >= itembuttons.length) {
    		return false
    	}
    	if (selectedIndex != undefined) {
	    	itembuttons[selectedIndex].activate(false)
    	}
   		onSelectEntry(itembuttons[entrynr])
   		selectedIndex = entrynr
    	itembuttons[selectedIndex].activate(true)
    	return true
    }
    
    /**
     * Shuffles the playlist
     */    public function shuffle() {
    	var mapper:Array = new Array();
    	for(var i:Number=0; i<itembuttons.length;i++) {
	    	mapper.push({nr: i, sort: Math.random()})
    	}
    	mapper.sortOn("sort");
    	var aNewEntry:/*WiiButton*/Array = new Array()
    	var newSelectedIndex:Number = undefined
    	for(var i:Number=0; i<mapper.length;i++) {
    		aNewEntry.push(itembuttons[mapper[i].nr])
    		if (selectedIndex == mapper[i].nr) {
		    	newSelectedIndex = i
    		}
    	}
    	itembuttons = aNewEntry
    	selectedIndex = newSelectedIndex
    	setCorrectCallbacksToButtons()
    	drawButtons()
    }
    
    public function selectNext(nr:Number):Boolean {
    	if (nr === undefined) {
    		if (selectedIndex === undefined) {
    			nr = 0
    		} else {
				nr = selectedIndex+1;
    		}
			if (nr >= itembuttons.length) {
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
    			nr = itembuttons.length-1
    		} else {
				nr = selectedIndex-1;
    		}
			if (nr < 0) {
	    		switch (mode) {
	    			case Playlist.PLAYLIST_MODE_SINGLE:
    					nr = undefined
    				break;
	    			case Playlist.PLAYLIST_MODE_REPEAT:
	    				nr = itembuttons.length-1
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
}