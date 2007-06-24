/*
 * Copyright (c) 2005 Pablo Costantini (www.luminicbox.com). All rights reserved.
 * 
 * Licensed under the MOZILLA PUBLIC LICENSE, Version 1.1 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.mozilla.org/MPL/MPL-1.1.html
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import LuminicBox.Log.IPublisher;
import LuminicBox.Log.LogEvent;
import LuminicBox.Utils.StringUtility;

/**
* Publishes logging messages into the OUTPUT window of the Macromedia Flash editor.<br />
* This publisher can only be used inside the Flash editor and uses the trace() command internally.
*/
class LuminicBox.Log.TracePublisher implements IPublisher {
	
	private var _maxDepth:Number;
	
	/**
	* Sets the max. inspection depth.<br />
	* The default value is 4.
	* The max. valid value is 255.
	*/
	function set maxDepth(value:Number) { _maxDepth = (_maxDepth>255)?255:value; }
	/**
	* Gets the max. inspection depth
	*/
	function get maxDepth():Number { return _maxDepth; }
	
	/**
	* Return the publishers type name: "TracePublisher".
	*/
	function toString():String { return "TracePublisher"; }	
	
	/**
	* Creates a TracePublisher instance with a default max. inspection depth of 4.
	*/
	function TracePublisher() {
		_maxDepth = 4;
	}
	
	/**
	* Logs a message into the OUTPUT window of the Flash editor.
	*/
	function publish(e:LogEvent):Void {
		var arg:Object = e.argument;
		var txt:String = "*" + e.level.toString() + "*";
		if(e.loggerId) txt += ":" + e.loggerId;
		txt += ":";
		txt += analyzeObj(arg,1);
		trace(txt);
	}

	private function analyzeObj(o,depth:Number):String {
		var txt:String = "";
		var typeOf:String = typeof(o);
		if(typeOf == "string") {
			// STRING
			txt += "\"" + o + "\"";
		} else if(typeOf == "boolean" || typeOf == "number") {
			// BOOLEAN / NUMBER
			txt += o;
		} else if(typeOf == "undefined" || typeOf == "null") {
			// UNDEFINED / NULL
			txt += "("+typeOf+")";
		} else {
			// OBJECT
			var stringifyObj:Boolean = false;
			var analize:Boolean = true;
			if(o instanceof Array) {
				// ARRAY
				typeOf = "array";
				stringifyObj = false;
			} else if(o instanceof Button) {
				// BUTTON
				typeOf = "button";
				stringifyObj = true;
			} else if(o instanceof Date) {
				// DATE
				typeOf = "date";
				analize = false;
				stringifyObj = true;
			} else if(o instanceof Color) {
				// COLOR
				typeOf = "color";
				analize = false;
				stringifyObj = true;
				o = o.getRGB().toString(16);
			} else if(o instanceof MovieClip) {
				// MOVIECLIP
				typeOf = "movieclip";
				stringifyObj = true;
			} else if(o instanceof XML) {
				// XML
				typeOf = "xml";
				analize = false;
				stringifyObj = true;
			} else if(o instanceof XMLNode) {
				// XML
				typeOf = "xmlnode";
				analize = false;
				stringifyObj = true;
			}
			txt += "(" + typeOf + ") ";
			if(stringifyObj) txt += o.toString();
			if(analize && depth <= _maxDepth) {
				var txtProps = "";
				for(var prop in o) {
					txtProps += "\n" +
						StringUtility.multiply( "\t", (depth+1) ) +
						prop + ":" +
						analyzeObj(o[prop], (depth+1) );
				}
				if(txtProps.length > 0) txt += "{" + txtProps + "\n" + StringUtility.multiply( "\t", depth ) + "}";
			}
		}
		return txt;
	}
}