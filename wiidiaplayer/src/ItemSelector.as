class ItemSelector {
	static public var __CLASS__:String = "ItemSelector";
	private var oLogger:LuminicBox.Log.Logger;

	private var itemselector_mc:MovieClip
	private var title_text:TextField
	private var close_btn:WiiButton
	private var next_btn:WiiButton
	private var up_btn:WiiButton
	private var add_btn:WiiButton
	private var previous_btn:WiiButton
	private var pagenr:Number

	private var itembuttons:/*WiiButton*/ Array
	private var visiblebuttons:/*WiiButton*/ Array
	
	private var callback:Function
	static private var countnr:Number=0;
	private var mycountnr:Number;

	public function ItemSelector(callback:Function) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		
		this.callback = callback
		
		pagenr = 0;
		itembuttons = new Array()
		visiblebuttons = new Array()
		mycountnr = ItemSelector.countnr++
	}
	
	/**
	 * Note: the ItemSelector will still be invisible when drawn, use the open method to show it
	 */
	public function draw(mc:MovieClip) {
		var self:ItemSelector = this
		mc.createEmptyMovieClip("itemselector_"+mycountnr, mc.getNextHighestDepth())
		itemselector_mc = mc["itemselector_"+mycountnr];
		itemselector_mc._x = Config.ITEMSELECTOR_X;
		itemselector_mc._y = Config.ITEMSELECTOR_Y;

		itemselector_mc.beginFill(0xcfcfdf);
		itemselector_mc.moveTo(0,0);
		itemselector_mc.lineTo(Config.ITEMSELECTOR_WIDTH,0);
		itemselector_mc.lineTo(Config.ITEMSELECTOR_WIDTH, Config.ITEMSELECTOR_HEIGHT);
		itemselector_mc.lineTo(0, Config.ITEMSELECTOR_HEIGHT);
		itemselector_mc.endFill()
		
		itemselector_mc.createTextField("title",itemselector_mc.getNextHighestDepth(),Config.ITEMSELECTOR_PADDING, Config.ITEMSELECTOR_PADDING, 0,0)
		title_text = itemselector_mc["title"];
		var tfmt:TextFormat = new TextFormat("defaultfont");
		tfmt.size=Config.ITEMSELECTOR_TITLE_FONTSIZE;
		tfmt.color=Config.ITEMSELECTOR_TITLE_FONTCOLOR;
		title_text.setNewTextFormat(tfmt)
		title_text.embedFonts=true;
		title_text.autoSize = "left"
		
		
		close_btn = new WiiButton("x", Config.ITEMSELECTOR_NAVBUTTON_WIDTH, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT)
		close_btn.draw(itemselector_mc, true)
		close_btn.setPosition(Config.ITEMSELECTOR_WIDTH-Config.ITEMSELECTOR_PADDING-Config.ITEMSELECTOR_NAVBUTTON_WIDTH*.5, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT/2+Config.ITEMSELECTOR_PADDING)
		close_btn.setClickHandler(function () {self.callback([]); self.close_btn.resetScale()})

		next_btn = new WiiButton(">>", Config.ITEMSELECTOR_NAVBUTTON_WIDTH, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT)
		next_btn.draw(itemselector_mc, false)
		next_btn.setPosition(Config.ITEMSELECTOR_WIDTH-Config.ITEMSELECTOR_PADDING*2-Config.ITEMSELECTOR_NAVBUTTON_WIDTH*1.5, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT/2+Config.ITEMSELECTOR_PADDING)
		next_btn.setClickHandler(function() {self.pagenr++; self.drawButtons()})

		previous_btn = new WiiButton("<<", Config.ITEMSELECTOR_NAVBUTTON_WIDTH, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT)
		previous_btn.draw(itemselector_mc, false)
		previous_btn.setPosition(Config.ITEMSELECTOR_WIDTH-Config.ITEMSELECTOR_PADDING*3-Config.ITEMSELECTOR_NAVBUTTON_WIDTH*2.5, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT/2+Config.ITEMSELECTOR_PADDING)
		previous_btn.setClickHandler(function() {self.pagenr--; self.drawButtons()})

		up_btn = new WiiButton("^^", Config.ITEMSELECTOR_NAVBUTTON_WIDTH, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT)
		up_btn.draw(itemselector_mc, false)
		up_btn.setPosition(Config.ITEMSELECTOR_WIDTH-Config.ITEMSELECTOR_PADDING*4-Config.ITEMSELECTOR_NAVBUTTON_WIDTH*3.5, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT/2+Config.ITEMSELECTOR_PADDING)
		
		add_btn = new WiiButton("+", Config.ITEMSELECTOR_NAVBUTTON_WIDTH, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT)
		add_btn.draw(itemselector_mc, true)
		add_btn.setPosition(Config.ITEMSELECTOR_WIDTH-Config.ITEMSELECTOR_PADDING*5-Config.ITEMSELECTOR_NAVBUTTON_WIDTH*4.5, Config.ITEMSELECTOR_NAVBUTTON_HEIGHT/2+Config.ITEMSELECTOR_PADDING)
		
		itemselector_mc._alpha = 80
		itemselector_mc._visible = false
		
		oLogger.info(itemselector_mc._parent)
	}
	
	public function open() {
		itemselector_mc._visible = true
	}
	
	public function close() {
		itemselector_mc._visible = false
	}
	
	public function setTitle(title:String) {
		title_text.text=title;
	}
	
	private function itemSelected(file:String) {
		callback([file])
	}
	
	private function drawButtons(){
		var btn:Object;
		while (btn = visiblebuttons.pop()) {
			btn.removeMovieClip();
		}
		var start:Number = pagenr*Config.ITEMSELECTOR_FILEBUTTON_NR_VERTICALLY*Config.ITEMSELECTOR_FILEBUTTON_NR_HORIZONTALLY
		var end:Number = Math.min(itembuttons.length, (pagenr+1)*Config.ITEMSELECTOR_FILEBUTTON_NR_VERTICALLY*Config.ITEMSELECTOR_FILEBUTTON_NR_HORIZONTALLY)
		for (var i:Number=start;i<end;i++) {
			itembuttons[i].draw(itemselector_mc, true)
			visiblebuttons.push(itembuttons[i])
			var pos:Object = this.getPositionForButton(i-start)
			itembuttons[i].setPosition(pos.x, pos.y)
		}
		
		next_btn.setEnabled(end < itembuttons.length)
		previous_btn.setEnabled(pagenr>0)
	}
	
	
	
	private function getPositionForButton(btnnr:Number):Object {
		var vertpos:Number = btnnr%Config.ITEMSELECTOR_FILEBUTTON_NR_VERTICALLY
		var horizonpos:Number = Math.floor(btnnr/Config.ITEMSELECTOR_FILEBUTTON_NR_VERTICALLY)
		var x:Number = Config.ITEMSELECTOR_PADDING*(horizonpos+1)+Config.ITEMSELECTOR_FILEBUTTON_WIDTH*(horizonpos+.5)
		var y:Number = Config.ITEMSELECTOR_HEADER_HEIGHT+Config.ITEMSELECTOR_PADDING*vertpos+Config.ITEMSELECTOR_FILEBUTTON_HEIGHT*(vertpos+.5)
		return {x:x, y:y}
	}
}