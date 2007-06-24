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

/**
* Publishes logging messages into the FlashInspector (if available)<br />
* This publisher can be used in any enviroment as long as the FlashInspector is running. It can be used from inside the Flash editor or from the final production enviroment. This allows to see the logging messages even after the final SWF is in production.
*/
class LuminicBox.Log.ConsolePublisher implements IPublisher {
	
	private var _version:Number=0.1;
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
	* Return the publishers type name: "ConsolePublisher".
	*/
	function toString():String { return "ConsolePublisher"; }
	
	/**
	* Creates a ConsolePublisher instance with a default max. inspection depth of 4.
	*/
	function ConsolePublisher() {
		_maxDepth = 4;
	}
	
	/**
	* Serializes and sends a log message to the FlashInspector window.
	*/
	function publish(e:LogEvent):Void {
		var o:Object = LogEvent.serialize(e);
		o.argument = serializeObj(o.argument,1);
		var lc:LocalConnection = new LocalConnection();
		lc.send("_luminicbox_log_console", "log", o);
	}
	
	private function serializeObj(o:Object,depth:Number):Object {
		var type:Object = getType(o);
		var serial:Object = new Object();
		if(!type.inspectable) {
			serial.value = o;
		} else if(type.stringify) {
			serial.value = o+"";
		} else {
			if(depth <= _maxDepth) {
				if(type.name == "movieclip" || type.name == "button") serial.id = o + "";
				var items:Array = new Array();
				if(o instanceof Array) {
					for(var pos:Number=0; pos<o.length; pos++) items.push( {property:pos,value:serializeObj( o[pos], (depth+1) )} );
				} else {
					for(var prop:String in o) items.push( {property:prop,value:serializeObj( o[prop], (depth+1) )} );
				}
				serial.value = items;
			} else {
				serial.reachLimit =true;
			}
		}
		serial.type = type.name;
		return serial;
	}
	
	
	private function getType(o:Object):Object {
		var typeOf:Object = typeof(o);
		var type:Object = new Object();
		type.inspectable = true;
		type.name = typeOf;
		if(typeOf == "string" || typeOf == "boolean" || typeOf == "number" || typeOf == "undefined" || typeOf == "null") {
			type.inspectable = false;
		} else if(o instanceof Date) {
			// DATE
			type.inspectable = false;
			type.name = "date";
		} else if(o instanceof Array) {
			// ARRAY
			type.name = "array";
		} else if(o instanceof Button) {
			// BUTTON
			type.name = "button";
		} else if(o instanceof MovieClip) {
			// MOVIECLIP
			type.name = "movieclip";
		} else if(o instanceof XML) {
			// XML
			type.name = "xml";
			type.stringify = true;
		} else if(o instanceof XMLNode) {
			// XML node
			type.name = "xmlnode"
			type.stringify = true;
		} else if(o instanceof Color) {
			// COLOR
			type.name = "color"
		}
		return type;
	}
}