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

/**
* This abtract class contains definitions for the message's levels.<br />
* The predefined levels are: ALL, LOG, DEBUG, INFO, WARN, ERROR, FATAL and NONE.
*/
class LuminicBox.Log.Level {
	
	/* private fields */
	private var _name:String;
	private var _value:Number;
	
	/* constructor*/
	private function Level(name:String, value:Number) {
		this._name = name;
		this._value = value;
	}	
	
	/**
	* The ALL level designates the lowest level possible. 
	*/
	static var ALL:Level = new Level("ALL", 1);
	/**
	* The LOG level designates fine-grained informational events.
	*/
	static var LOG:Level = new Level("LOG", 1);
	/**
	* The DEBUG level designates fine-grained debug information.
	*/
	static var DEBUG:Level = new Level("DEBUG", 2);
	/**
	* The INFO level designates informational messages that highlight the progress of the application at coarse-grained level.
	*/
	static var INFO:Level = new Level("INFO",4);
	/**
	* The WARN level designates potentially harmful situations. 
	*/
	static var WARN:Level = new Level("WARN",8);
	/**
	* The ERROR level designates error events that might still allow the application to continue running. 
	*/
	static var ERROR:Level = new Level("ERROR",16);
	/**
	* The FATAL level designates very severe error events that will presumably lead the application to abort or stop. 
	*/
	static var FATAL:Level = new Level("FATAL",32);
	/**
	* The NONE level when used with setLevel makes all messages to be ignored.
	*/
	static var NONE:Level = new Level("NONE", 1024);
	
	//public static var INSPECT:Level = new Level("INSPECT", 0);
	
	/**
	* Returns the level's name.
	*/
	function getName():String { return _name; }
	/**
	* Returns the level's bitwise value.
	*/
	function getValue():Number { return _value; }
	/**
	* Return the level's name.
	*/
	function toString():String { return getName(); }
}