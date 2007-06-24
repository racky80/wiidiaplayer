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

import LuminicBox.Log.Level;
import LuminicBox.Log.IPublisher;
import LuminicBox.Log.LogEvent;

/**
* Main Class.<br />
* This class contains methods for logging messages at differente levels.<br />
* These messages can me basic types (strings, numbers, dates) or complex objects and MovieClips.<br />
* There are also configuration methods.
* <h4>Example:</h4>
* <pre>
* 	import LuminicBox.Log.*;<br />
* 	var log = new Logger();<br />
* 	log.addPublisher( new TracePublisher() );<br />
* 	// ...<br />
* 	log.debug("debug message");<br />
* 	log.info("info message");<br />
* 	// ...<br />
* 	var xml = new XML("&lt;note&gt;&lt;to&gt;John&lt;/to&gt;&lt;from&gt;Dana&lt;/from&gt;&lt;heading&gt;Reminder&lt;/heading&gt;&lt;body&gt;Don&acute;t forget the milk&lt;/body&gt;&lt;/note&gt;");<br/>
* 	log.debug(xml);<br />
* </pre>
*/
class LuminicBox.Log.Logger {
	
	private var _loggerId:String;
	private var _publishers:Array;
	private var _filters:Array;
	private var _level:Level;
	
	/**
	* Sets the lowest required level for any message.<br />
	* Any message that have a level that is lower than the supplied value will be ignored.<br />
	* This is the most basic form of filter.
	*/
	function setLevel(level:Level):Void { _level = level; }
	
	/**
	* Creates a new Logger instance.<br />
	* The logId parameter is optional. It identifies the logger and all messages to the publisher will be sent with this ID.
	* @param logId String (optional)
	*/
	function Logger(logId:String) {
		if(logId && logId.length > 0) this._loggerId = logId;
		this._level = Level.LOG;
		_publishers = new Array();
		_filters = new Array();
	}
	
	/**
	* Adds a Publisher to the publishers collection. The supplied publisher must implement the IPublisher interface<br />
	* There can only be one instance of each Publisher.
	*/
	function addPublisher(publisher:IPublisher):Void {
		if( !_publishers[publisher.toString()] ) _publishers[publisher.toString()] = publisher
	}
	/**
	* Removes a Publisher from the publishers collection. A new instance of that kind of publisher can be supplied.
	*/
	function removePublisher(publisher:IPublisher):Void {
		delete _publishers[publisher.toString()];
	}
	/**
	* Return the publishers collection.
	*/
	function getPublishers():Array { return _publishers; }
	
	/*public function addFilter(filter:IFilter):Void {
		if( !_filters[filter.toString()] ) _filters[filter.toString()] = filter;
	}
	public function removeFilter(filter:IFilter):Void {
		delete _filters[filter.toString()];
	}*/
	
	private function publish(argument:Object, level:Level):Void {
		if( level.getValue() >= _level.getValue() ) {
			var e:LogEvent = new LogEvent(this._loggerId, argument, level);
			for(var publisher:String in _publishers) {
				IPublisher(_publishers[publisher]).publish(e);
			}
		}
	}
	
	/* log functions */
	/**
	* Logs an object or message with the LOG level.
	* @param argument The message or object to inspect.
	*/
	function log(argument:Object):Void { publish(argument, Level.LOG); }
	/**
	* Logs an object or message with the DEBUG level.
	* @param argument The message or object to inspect.
	*/	
	function debug(argument:Object):Void { publish(argument, Level.DEBUG); }
	/**
	* Logs an object or message with the INFO level.
	* @param argument The message or object to inspect.
	*/
	function info(argument:Object):Void { publish(argument, Level.INFO); }
	/**
	* Logs an object or message with the WARN level.
	* @param argument The message or object to inspect.
	*/	
	function warn(argument:Object):Void { publish(argument, Level.WARN); }
	/**
	* Logs an object or message with the ERROR level.
	* @param argument The message or object to inspect.
	*/	
	function error(argument:Object):Void { publish(argument, Level.ERROR); }
	/**
	* Logs an object or message with the FATAL level.
	* @param argument The message or object to inspect.
	*/	
	function fatal(argument:Object):Void { publish(argument, Level.FATAL); }
	
	//function inspect(argument):Void { publish(argument, Level.INSPECT); }
	
}