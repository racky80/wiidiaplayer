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
	
	private var enabled_tf:TextFormat;
	private var disabled_tf:TextFormat;
	private var enabled:Boolean;
	
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
		
		enabled_tf = new TextFormat("defaultfont");
		enabled_tf.size=Config.WIIBUTTON_ENABLED_FONTSIZE
		enabled_tf.color=Config.WIIBUTTON_ENABLED_FONTCOLOR

		disabled_tf = new TextFormat("defaultfont");
		disabled_tf.size=Config.WIIBUTTON_DISABLED_FONTSIZE
		disabled_tf.color=Config.WIIBUTTON_DISABLED_FONTCOLOR
		
		enabled=null
	}
	
	public function draw(mc:MovieClip, enabled:Boolean) {
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
		button_text.embedFonts=true;
		button_text.setNewTextFormat(enabled_tf)
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
		
		drawn = true
		this.setEnabled(enabled, true)
	}
	
	public function setPosition(x:Number, y:Number) {
		button_mc._x = x;
		button_mc._y = y;
	}
	
	public function setClickHandler(handler:Function) {
		this.handler = handler
		if (drawn && enabled) {
			button_mc.onPress = handler
		}
	}
	
	public function resetScale() {
		button_mc.targetscaling=100;
	}
	
	public function removeMovieClip() {
		button_mc.removeMovieClip()
	}
	
	public function setEnabled(value:Boolean, force:Boolean) {
		if (this.enabled == value && !force) {
			return;
		}
		this.enabled = value;
		if (this.enabled) {
			button_text.setTextFormat(enabled_tf);
			WiiButton.makeIntoGrowingButton(button_mc)
			button_mc.onPress = handler
		} else {
			button_text.setTextFormat(disabled_tf);
			WiiButton.disableGrowingButton(button_mc)
			button_mc.onPress = null
		}
	}
	
	public function activate(activate:Boolean) {
        var tfmt:TextFormat = button_text.getNewTextFormat();
        if (activate) {
        	tfmt.color=Config.WIIBUTTON_ACTIVE_FONTCOLOR
        	tfmt.size=Config.WIIBUTTON_ACTIVE_FONTSIZE
        } else {
        	tfmt.color=Config.WIIBUTTON_ENABLED_FONTCOLOR
        	tfmt.size=Config.WIIBUTTON_ENABLED_FONTSIZE
        }
        this.button_text.setTextFormat(tfmt)
	}

	static function makeIntoGrowingButton(mc:MovieClip) {
		var oLogger:LuminicBox.Log.Logger = new LuminicBox.Log.Logger(__CLASS__);
		oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );

		
		mc.targetscaling = 100;
		mc.currentscaling = mc.targetscaling;

		mc.onRollOut = function() {
			mc.targetscaling = 100;
		}
		
		WiiButton.enableGrowingButton(mc)
		
	}
	
	
	static function enableGrowingButton(mc:MovieClip) {
		var oLogger:LuminicBox.Log.Logger = new LuminicBox.Log.Logger(__CLASS__);
		oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		mc.onRollOver = function() {
			// put this button on the top of the pile
			mc.swapDepths(mc._parent.getNextHighestDepth()-1)
			mc.targetscaling = Config.WIIBUTTON_MAXSCALE;

			mc.onEnterFrame = function () {
				if (!mc.hitTest(_root._xmouse,_root._ymouse)) {
					mc.targetscaling=100;
				}
				if (mc.currentscaling != mc.targetscaling) {
					var diff:Number = Math.max(Math.min(mc.targetscaling-mc.currentscaling, Config.WIIBUTTON_SCALE_SPEED), -Config.WIIBUTTON_SCALE_SPEED);
					mc._xscale += diff;
					mc._yscale += diff;
					mc.currentscaling += diff;
				} else if (this.currentscaling == 100) {
					mc.onEnterFrame=undefined; // resetting this handler after we're done
				}
			}
		}
	}

	
	static function disableGrowingButton(mc:MovieClip) {
		mc.onRollOver = null
	}

}