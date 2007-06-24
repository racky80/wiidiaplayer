/**
 * @author reinoud
 */
class Config {
	static var RTMP_SERVER_URL:String = "rtmp://10.1.0.20";
	static var RTMP_TESTFLV:String = "simps-0000";

	static var TITLEBAR_FONTSIZE:Number=30;
	static var TITLEBAR_FONTCOLOR:Number=0xdfdfff;
	static var TITLEBAR_PADDING:Number=15;
	static var TITLEBAR_TIMEOUT:Number=5000;
	static var TITLEBAR_MAX_ALPHA:Number=80;
	static var TITLEBAR_APPEAR_SPEED:Number=10;
	static var TITLEBAR_DISAPPEAR_SPEED:Number=5;
	
	static var WIIBUTTON_MAXSCALE:Number=150;
	static var WIIBUTTON_SCALE_SPEED:Number=15;

	static var WIIBUTTON_FONTSIZE:Number=15;
	static var WIIBUTTON_FLASHINTERNAL_TEXTFIELD_PADDING:Number=Config.WIIBUTTON_FONTSIZE*.15;
	static var WIIBUTTON_FONTCOLOR:Number=0x000000;
	static var WIIBUTTON_PADDING:Number=3;
	
	static var FILESELECTOR_X:Number = 50
	static var FILESELECTOR_Y:Number = 50
	static var FILESELECTOR_WIDTH:Number = Stage.width-2*Config.FILESELECTOR_X
	static var FILESELECTOR_HEIGHT:Number = Stage.height-Config.FILESELECTOR_Y
	
}