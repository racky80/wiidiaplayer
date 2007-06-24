class Util {
	
	static public function basename(path:String):String {
		var aPath:Array;
		aPath = path.split('/')
		return  String(aPath.pop());
	}
	
}