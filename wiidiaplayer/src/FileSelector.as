class FileSelector {
	static public var __CLASS__:String = "FileSelector";
	private var oLogger:LuminicBox.Log.Logger;
	
	private var currentpath:String
	private var fileselector_mc:MovieClip
	private var title_text:TextField
	private var up_btn:WiiButton
	private var close_btn:WiiButton
	private var next_btn:WiiButton
	private var previous_btn:WiiButton
	private var pagenr:Number

	private var filebuttons:/*WiiButton*/ Array
	private var visiblebuttons:/*WiiButton*/ Array
	
	private var callback:Function

	public function FileSelector(callback:Function) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		
		this.callback = callback
		
		pagenr = 0;
		filebuttons = new Array()
		visiblebuttons = new Array()
	}
	
	/**
	 * Note: the FileSelector will still be invisible when drawn, use the open method to show it	 */
	public function draw(mc:MovieClip) {
		var self:FileSelector = this
		mc.createEmptyMovieClip("fileselector", mc.getNextHighestDepth())
		fileselector_mc = mc["fileselector"];
		fileselector_mc._x = Config.FILESELECTOR_X;
		fileselector_mc._y = Config.FILESELECTOR_Y;

		fileselector_mc.beginFill(0xcfcfdf);
		fileselector_mc.moveTo(0,0);
		fileselector_mc.lineTo(Config.FILESELECTOR_WIDTH,0);
		fileselector_mc.lineTo(Config.FILESELECTOR_WIDTH, Config.FILESELECTOR_HEIGHT);
		fileselector_mc.lineTo(0, Config.FILESELECTOR_HEIGHT);
		fileselector_mc.endFill()
		
		fileselector_mc.createTextField("title",fileselector_mc.getNextHighestDepth(),Config.FILESELECTOR_PADDING, Config.FILESELECTOR_PADDING, 0,0)
		title_text = fileselector_mc["title"];
		var tfmt:TextFormat = new TextFormat("defaultfont");
		tfmt.size=Config.FILESELECTOR_TITLE_FONTSIZE;
		tfmt.color=Config.FILESELECTOR_TITLE_FONTCOLOR;
		title_text.setNewTextFormat(tfmt)
		title_text.embedFonts=true;
		title_text.autoSize = "left"
		
		
		close_btn = new WiiButton("x", Config.FILESELECTOR_NAVBUTTON_WIDTH, Config.FILESELECTOR_NAVBUTTON_HEIGHT)
		close_btn.draw(fileselector_mc, true)
		close_btn.setPosition(Config.FILESELECTOR_WIDTH-Config.FILESELECTOR_PADDING-Config.FILESELECTOR_NAVBUTTON_WIDTH*.5, Config.FILESELECTOR_NAVBUTTON_HEIGHT/2+Config.FILESELECTOR_PADDING)
		close_btn.setClickHandler(function () {self.callback(""); self.close_btn.resetScale()})
		next_btn = new WiiButton(">>", Config.FILESELECTOR_NAVBUTTON_WIDTH, Config.FILESELECTOR_NAVBUTTON_HEIGHT)
		next_btn.draw(fileselector_mc, false)
		next_btn.setPosition(Config.FILESELECTOR_WIDTH-Config.FILESELECTOR_PADDING*2-Config.FILESELECTOR_NAVBUTTON_WIDTH*1.5, Config.FILESELECTOR_NAVBUTTON_HEIGHT/2+Config.FILESELECTOR_PADDING)
		next_btn.setClickHandler(function() {self.pagenr++; self.drawButtons()})
		previous_btn = new WiiButton("<<", Config.FILESELECTOR_NAVBUTTON_WIDTH, Config.FILESELECTOR_NAVBUTTON_HEIGHT)
		previous_btn.draw(fileselector_mc, false)
		previous_btn.setPosition(Config.FILESELECTOR_WIDTH-Config.FILESELECTOR_PADDING*3-Config.FILESELECTOR_NAVBUTTON_WIDTH*2.5, Config.FILESELECTOR_NAVBUTTON_HEIGHT/2+Config.FILESELECTOR_PADDING)
		previous_btn.setClickHandler(function() {self.pagenr--; self.drawButtons()})
		up_btn = new WiiButton("^^", Config.FILESELECTOR_NAVBUTTON_WIDTH, Config.FILESELECTOR_NAVBUTTON_HEIGHT)
		up_btn.draw(fileselector_mc, false)
		up_btn.setPosition(Config.FILESELECTOR_WIDTH-Config.FILESELECTOR_PADDING*4-Config.FILESELECTOR_NAVBUTTON_WIDTH*3.5, Config.FILESELECTOR_NAVBUTTON_HEIGHT/2+Config.FILESELECTOR_PADDING)
		up_btn.setClickHandler(function() {self.retrieveAndShowDirContents(Util.dirname(self.currentpath))})
		
		
		fileselector_mc._alpha = 80
		fileselector_mc._visible = false
		
		oLogger.info(fileselector_mc._parent)
		
		// couldn't retrieve them before...
		retrieveAndShowDirContents('/')
	}
	
	public function open() {
		fileselector_mc._visible = true
	}
	
	public function close() {
		fileselector_mc._visible = false
	}
	
	public function setTitle(title:String) {
		title_text.text=title;
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
		filebuttons = new Array()
		oLogger.info(asDir)
		for(var i:Number=0;i<asDir.length;i++) {
			var sDir:Object = asDir[i]
			var btn:WiiButton = new WiiButton(sDir["name"], Config.FILESELECTOR_FILEBUTTON_WIDTH, Config.FILESELECTOR_FILEBUTTON_HEIGHT)
			if (sDir["type"] == 'file') {
				btn.setClickHandler(function (file:String, mybtn:WiiButton):Function {return function() {self.fileSelected(file); mybtn.resetScale(); }}(self.currentpath+sDir["name"], btn))
			}else { //dir
				btn.setClickHandler(function (dir:String):Function {return function() {self.retrieveAndShowDirContents(dir) }}(self.currentpath+sDir["name"]+'/'))
			}
			filebuttons.push(btn)
		}
		pagenr= 0;
		this.drawButtons()
	}
	
	private function fileSelected(file:String) {
		callback(file)
	}
	
	private function drawButtons(){
		this.setTitle(currentpath+"("+(pagenr+1)+")")
		var btn:Object;
		while (btn = visiblebuttons.pop()) {
			btn.removeMovieClip();
		}
		var start:Number = pagenr*Config.FILESELECTOR_FILEBUTTON_NR_VERTICALLY*Config.FILESELECTOR_FILEBUTTON_NR_HORIZONTALLY
		var end:Number = Math.min(filebuttons.length, (pagenr+1)*Config.FILESELECTOR_FILEBUTTON_NR_VERTICALLY*Config.FILESELECTOR_FILEBUTTON_NR_HORIZONTALLY)
		for (var i:Number=start;i<end;i++) {
			filebuttons[i].draw(fileselector_mc, true)
			visiblebuttons.push(filebuttons[i])
			var pos:Object = this.getPositionForButton(i-start)
			filebuttons[i].setPosition(pos.x, pos.y)
		}
		
		next_btn.setEnabled(end < filebuttons.length)
		previous_btn.setEnabled(pagenr>0)
		up_btn.setEnabled(currentpath != "/")
	}
	
	
	
	private function getPositionForButton(btnnr:Number):Object {
		var vertpos:Number = btnnr%Config.FILESELECTOR_FILEBUTTON_NR_VERTICALLY
		var horizonpos:Number = Math.floor(btnnr/Config.FILESELECTOR_FILEBUTTON_NR_VERTICALLY)
		var x:Number = Config.FILESELECTOR_PADDING*(horizonpos+1)+Config.FILESELECTOR_FILEBUTTON_WIDTH*(horizonpos+.5)
		var y:Number = Config.FILESELECTOR_HEADER_HEIGHT+Config.FILESELECTOR_PADDING*vertpos+Config.FILESELECTOR_FILEBUTTON_HEIGHT*(vertpos+.5)
		return {x:x, y:y}
	}
}