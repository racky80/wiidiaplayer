class Dragger {
	static public var __CLASS__:String = "Dragger";
	private var oLogger:LuminicBox.Log.Logger;
	
	private var startcallback:Function
	private var endcallback:Function
	private var movementcallback:Function
	
	private var dragstartpos:Object = null
	private var isdragging:Boolean
	
	private var movementlistener:Object
	
	public function Dragger(startcallback:Function, endcallback:Function, movementcallback:Function) {
		this.oLogger = new LuminicBox.Log.Logger(__CLASS__);
		this.oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		this.oLogger.info("__init__ "+__CLASS__);
		
		this.startcallback = startcallback
		this.endcallback = endcallback
		this.movementcallback=movementcallback
		
		this.init();
	}
	
	private function init() {
		var self:Dragger = this
		Mouse.addListener({
				onMouseDown: function() {self.startDrag()},
				onMouseUp: function() {self.endDrag()}
			})
		movementlistener = {
			onMouseMove:function() {self.checkMovement()}
		}
	}
	
	private function checkMovement() {
		if (!isdragging) {
			var diff:Object = getPosDifferentFromStart()
			if (diff["x"]*diff["x"]+diff["y"]+diff["y"] > Config.DRAGGER_SENSIBILITY) {
				isdragging = true
				startcallback()
			}
		}
		if (isDragActive()) {
			var relpos:Object = getDragDistance();
			movementcallback(relpos["x"], relpos["y"])
		}
	}
	
	private function startDrag() {
		dragstartpos = {x:_root._xmouse, y:_root._ymouse}
		isdragging = false
		Mouse.addListener(movementlistener)
	}
	
	private function endDrag() {
		Mouse.removeListener(movementlistener)
		if (!isDragActive()) {
			return
		}
		var relpos:Object = getDragDistance();
		endcallback(relpos["x"], relpos["y"])
		dragstartpos = null
	}
	
	public function getDragDistance():Object {
		if (!isDragActive()) {
			return {x: 0, y: 0}
		}
		return getPosDifferentFromStart()
	}
	
	private function getPosDifferentFromStart():Object {
		var pos:Object = {x:_root._xmouse, y:_root._ymouse}
		return {x: pos["x"]- dragstartpos["x"], y: pos["y"]- dragstartpos["y"]}
	}
	
	function isDragActive():Boolean {
		return dragstartpos!= null && isdragging
	}
	
}