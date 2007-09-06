class Util {
	
	static public function dirname(path:String):String {
		var aPath:Array = path.split('/')
		return  aPath.slice(0,-2).join('/')+'/';
	}
	
	static public function basename(path:String):String {
		var aPath:Array = path.split('/')
		return  String(aPath.pop());
	}
	
	/**
	 * Parses the result of an ls -l, returns an array with entries of the form:
	 * type: file/dir; name: 	 */
	static public function parseLS(ls:String):Array {
		var oLogger:LuminicBox.Log.Logger = new LuminicBox.Log.Logger("UTIL.parseLS");
		oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );

		var asDir:Array = [];
		var aLine:Array = ls.split("\n");
		for(var i:Number=1;i<aLine.length;i++) { // ignore the first line "total"
			var line:String = String(aLine[i])
			if (line == "") {
				continue;
			}
			var fieldcount:Number = 0;
			var aPart:Array = line.split(" ");
			
			for(var j:Number=0;j<aPart.length;j++) {
				if (aPart[j] != "") {
					fieldcount++
				}
				if (fieldcount == 9) {
					// we are now at the beginnig of the name
					var filename:String = aPart.slice(j).join(" ")
					var type:String = (line.charAt(0) == 'd'?"dir":"file")
					asDir.push({type: type, name:filename})
				}
			}
		}
		return asDir;
	}
	
	static public function formatAsTime(timeseconds:Number):String {
		var hours:Number = Math.floor(timeseconds/3600)
		var minutes:Number = Math.floor(timeseconds/60)%60
		var seconds:Number = Math.floor(timeseconds)%60
		var s:String = ""
		if (hours) {
			s+= hours+":"
		}
		return s+Util.formatAsTwoDigits(minutes)+":"+Util.formatAsTwoDigits(seconds)
	}

	static public function formatAsTwoDigits(n:Number):String {
		if (n < 10) {
			return "0"+Math.floor(n)
		}
		return ""+Math.floor(n%100)
	}
	
	static function sendFeedback(s:String) {
		if (!_root.lv) {
			_root.lv = new Array();
		}
		var lv:LoadVars = new LoadVars()
		lv.load('/feedback/'+escape(s))
		_root.lv.append(lv)
	}
	
	
	
	
}