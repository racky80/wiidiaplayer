class WiiButton extends MovieClip {
	static public var __CLASS__:String = "WiiButton";
	static public var count:Number = 0;
	private var oLogger:LuminicBox.Log.Logger;
	
	private var text:String;
	private var width:Number;
	private var height:Number;
	private var thiscount:Number;
	private var handler:Function;
	private var drawn:Boolean;
	

	private var button_mc:MovieClip;
	private var button_text:TextField;
	
	public function WiiButton(text:String, width:Number, height:Number) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.setLevel(Config.GLOBAL_LOGLEVEL)
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.debug("__init__ "+__CLASS__+"("+text+")");
		thiscount=WiiButton.count++;
		
		this.text = text
		this.width = width
		this.height = height
		drawn = false
	}
	
	public function draw(mc:MovieClip) {
		mc.createEmptyMovieClip("wiibutton_"+thiscount,mc.getNextHighestDepth());
		button_mc = mc["wiibutton_"+thiscount];
		
		button_mc.lineStyle(1, 0x3f3fff)
		button_mc.beginFill(0xafafcf);
		button_mc.moveTo(-width/2,-height/2);
		button_mc.lineTo(width/2,-height/2);
		button_mc.lineTo(width/2,height/2);
		button_mc.lineTo(-width/2,height/2);
		button_mc.endFill();
		
		button_mc.createTextField("mytext",button_mc.getNextHighestDepth(),-width/2+Config.WIIBUTTON_PADDING,-height/2+Config.WIIBUTTON_PADDING, width-2*Config.WIIBUTTON_PADDING, height-2*Config.WIIBUTTON_PADDING)
		button_text = button_mc["mytext"];
		var tfmt:TextFormat = new TextFormat("defaultfont");
		tfmt.size=Config.WIIBUTTON_FONTSIZE;
		tfmt.color=Config.WIIBUTTON_FONTCOLOR;
		button_text.setNewTextFormat(tfmt)
		button_text.embedFonts=true;
		button_text.text=text;
		var fieldWidth:Number = button_text.textWidth+2* Config.WIIBUTTON_FLASHINTERNAL_TEXTFIELD_PADDING
		var fieldHeight:Number = button_text.textHeight+2* Config.WIIBUTTON_FLASHINTERNAL_TEXTFIELD_PADDING
		if (fieldWidth > width-2*Config.WIIBUTTON_PADDING) {
			var nrchars:Number = text.length;
			while (button_text.textWidth+2* Config.WIIBUTTON_FLASHINTERNAL_TEXTFIELD_PADDING > width-2*Config.WIIBUTTON_PADDING) {
				nrchars--;
				button_text.text = text.substr(0,nrchars)+"...";
			}
			fieldWidth = button_text.textWidth+2* Config.WIIBUTTON_FLASHINTERNAL_TEXTFIELD_PADDING
		}
		button_text._x=-fieldWidth/2
		button_text._width=fieldWidth
		
		button_text._y=Math.max(button_text._y, -fieldHeight/2)
		button_text._height=Math.min(button_text._height,fieldHeight)
		
		WiiButton.makeIntoGrowingButton(button_mc);
		// now get the button into place
		
		drawn = true
		button_mc.onPress = handler
	}
	
	public function setPosition(x:Number, y:Number) {
		button_mc._x = x;
		button_mc._y = y;
	}
	
	public function setClickHandler(handler:Function) {
		this.handler = handler
		if (drawn) {
			button_mc.onPress = handler
		}
	}
	
	public function removeMovieClip() {
		button_mc.removeMovieClip()
	}
	
	static function makeIntoGrowingButton(mc:MovieClip) {
		var oLogger:LuminicBox.Log.Logger = new LuminicBox.Log.Logger(__CLASS__);
		oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );

		
		mc.targetscaling = 100;
		mc.currentscaling = mc.targetscaling;
		mc.onEnterFrame = function () {
			if (this.currentscaling != this.targetscaling) {
				var diff:Number = Math.max(Math.min(this.targetscaling-this.currentscaling, Config.WIIBUTTON_SCALE_SPEED), -Config.WIIBUTTON_SCALE_SPEED);
				this._xscale += diff;
				this._yscale += diff;
				this.currentscaling += diff;
			}
		}

		mc.onRollOver = function() {
			// put this button on the top of the pile
			this.swapDepths(this._parent.getNextHighestDepth()-1)
			this.targetscaling = Config.WIIBUTTON_MAXSCALE;
		}

		mc.onRollOut = function() {
			this.targetscaling = 100;
		}
		
	}
}