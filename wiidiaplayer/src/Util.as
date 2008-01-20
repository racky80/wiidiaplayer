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
	static public function parseGetDir(getdirresult:String):Array {
		var oLogger:LuminicBox.Log.Logger = new LuminicBox.Log.Logger("UTIL.parseGetDir");
		oLogger.addPublisher( new LuminicBox.Log.ConsolePublisher() );
		var json:JSON = new JSON();
		var sDirInfo:Object = json.parse(getdirresult);
		var asDir:Array = [];
		for(var i:Number=0;i<sDirInfo["aDir"].length;i++) {
			asDir.push({type: "dir", name: sDirInfo["aDir"][i]})
		}
		for(var i:Number=0;i<sDirInfo["aFile"].length;i++) {
			asDir.push({type: "file", name: sDirInfo["aFile"][i]})
		}
		return asDir
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