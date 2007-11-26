class FileSelector extends ItemSelector {
	static public var __CLASS__:String = "FileSelector";

	private var currentpath:String
	private var up_btn:WiiButton
	private var add_btn:WiiButton
	private var aFilename:/*String*/Array //contains all files shown in this directory (not the directories, or in the subdirectories)
	
	public function FileSelector(callback:Function) {
		super(callback)
	}

	/**
	 * Note: the FileSelector will still be invisible when drawn, use the open method to show it	 */
	public function draw(mc:MovieClip) {
		super.draw(mc)
		var self:FileSelector = this
		up_btn.setClickHandler(function() {self.retrieveAndShowDirContents(Util.dirname(self.currentpath))})
		add_btn.setClickHandler(function() {self.callback(self.aFilename)})
		
		// couldn't retrieve them before...
		retrieveAndShowDirContents('/')
	}
	
	private function retrieveAndShowDirContents(newpath:String) {
		this.currentpath = newpath
		var lv:LoadVars = new LoadVars()
		var self:FileSelector = this;
		lv.onLoad = function (success:Boolean) {
			if (! success) {
				self.setTitle("Error retrieving "+self.currentpath)
				return;
			}
			if (self.currentpath != newpath) { // some other dir must have been selected in the meantime
				return
			}
			self.showDirContents(Util.parseLS(this.result))
		}
		lv.load(Config.GETDIR_SERVER_URL+currentpath)
	}
	
	
	private function showDirContents(asDir:Array) {
		var self:FileSelector = this
		itembuttons = new Array()
		aFilename = new Array()
//		oLogger.info(asDir)
		for(var i:Number=0;i<asDir.length;i++) {
			var sDir:Object = asDir[i]
			var btn:WiiButton = new WiiButton(sDir["name"], Config.ITEMSELECTOR_FILEBUTTON_WIDTH, Config.ITEMSELECTOR_FILEBUTTON_HEIGHT)
			if (sDir["type"] == 'file') {
				aFilename.push(self.currentpath+sDir["name"])
				btn.setClickHandler(function (file:String, mybtn:WiiButton):Function {return function() {self.itemSelected(file); mybtn.resetScale(); }}(self.currentpath+sDir["name"], btn))
			}else { //dir
				btn.setClickHandler(function (dir:String):Function {return function() {self.retrieveAndShowDirContents(dir) }}(self.currentpath+sDir["name"]+'/'))
			}
			itembuttons.push(btn)
		}
		pagenr= 0;
		this.drawButtons()
	}
	
	private function drawButtons(){
		super.drawButtons();
		this.setTitle(currentpath+"("+(pagenr+1)+")")
		up_btn.setEnabled(currentpath != "/")
	}
	
}