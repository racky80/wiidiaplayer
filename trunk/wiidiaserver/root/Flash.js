
/*
Macromedia(r) Flash(r) JavaScript Integration Kit License


Copyright (c) 2005 Macromedia, inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. The end-user documentation included with the redistribution, if any, must
include the following acknowledgment:

"This product includes software developed by Macromedia, Inc.
(http://www.macromedia.com)."

Alternately, this acknowledgment may appear in the software itself, if and
wherever such third-party acknowledgments normally appear.

4. The name Macromedia must not be used to endorse or promote products derived
from this software without prior written permission. For written permission,
please contact devrelations@macromedia.com.

5. Products derived from this software may not be called "Macromedia" or
"Macromedia Flash", nor may "Macromedia" or "Macromedia Flash" appear in their
name.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MACROMEDIA OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

--

This code is part of the Flash / JavaScript Integration Kit:
http://www.macromedia.com/go/flashjavascript/

Created by:

Christian Cantrell
http://weblogs.macromedia.com/cantrell/
mailto:cantrell@macromedia.com

Mike Chambers
http://weblogs.macromedia.com/mesh/
mailto:mesh@macromedia.com

Macromedia
*/

/**
 * Create a new Exception object.
 * name: The name of the exception.
 * message: The exception message.
 */
function Exception(name, message)
{
    if (name)
        this.name = name;
    if (message)
        this.message = message;
}

/**
 * Set the name of the exception. 
 */
Exception.prototype.setName = function(name)
{
    this.name = name;
}

/**
 * Get the exception's name. 
 */
Exception.prototype.getName = function()
{
    return this.name;
}

/**
 * Set a message on the exception. 
 */
Exception.prototype.setMessage = function(msg)
{
    this.message = msg;
}

/**
 * Get the exception message. 
 */
Exception.prototype.getMessage = function()
{
    return this.message;
}



/*
Macromedia(r) Flash(r) JavaScript Integration Kit License


Copyright (c) 2005 Macromedia, inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. The end-user documentation included with the redistribution, if any, must
include the following acknowledgment:

"This product includes software developed by Macromedia, Inc.
(http://www.macromedia.com)."

Alternately, this acknowledgment may appear in the software itself, if and
wherever such third-party acknowledgments normally appear.

4. The name Macromedia must not be used to endorse or promote products derived
from this software without prior written permission. For written permission,
please contact devrelations@macromedia.com.

5. Products derived from this software may not be called "Macromedia" or
"Macromedia Flash", nor may "Macromedia" or "Macromedia Flash" appear in their
name.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MACROMEDIA OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

--

This code is part of the Flash / JavaScript Integration Kit:
http://www.macromedia.com/go/flashjavascript/

Created by:

Christian Cantrell
http://weblogs.macromedia.com/cantrell/
mailto:cantrell@macromedia.com

Mike Chambers
http://weblogs.macromedia.com/mesh/
mailto:mesh@macromedia.com

Macromedia
*/

/**
 * The FlashProxy object is what proxies function calls between JavaScript and Flash.
 * It handles all argument serialization.
 */

/**
 * Instantiates a new FlashProxy object.
 * lcId: Each FlashProxy needs a unique lcId. This will need to get passed into your Flash content, as well.
 * flashId: the ID or name of your Flash content. This is required to make FSCommand work.
 * proxySwfName: the name (including the path) of the Flash proxy SWF.
 * callbackScope (optional): The scope where you want calls from Flash to JavaScript to go. This argument
 * is optional. If you leave it out, calls will be made on the document level.
 */
function FlashProxy(lcId, flashId, proxySwfName, callbackScope)
{
	FlashProxy.fpmap[lcId] = this;
    this.uid = lcId;
    this.proxySwfName = proxySwfName;
    this.callbackScope = callbackScope;
    this.flashSerializer = new FlashSerializer(false);
    this.q = new Array();

    if (navigator.appName.indexOf ('Internet Explorer') != -1 &&
        navigator.platform.indexOf('Win') != -1 &&
        navigator.userAgent.indexOf('Opera') == -1)
    {
	    setUpVBCallback(flashId);
	}
    
}

/**
 * Call a function in your Flash content.  Arguments should be:
 * 1. ActionScript function name to call,
 * 2. any number of additional arguments of type object,
 *    array, string, number, boolean, date, null, or undefined. 
 */
FlashProxy.prototype.call = function()
{
    if (arguments.length == 0)
    {
        throw new Exception("Flash Proxy Exception",
                            "The first argument should be the function name followed by any number of additional arguments.");
    }
    
    this.q.push(arguments);
    
    if (this.q.length == 1)
    {
		this._execute(arguments);
    }
}

/**
 * "Private" function.  Don't call.
 */
FlashProxy.prototype._execute = function(args)
{
    var ft = new FlashTag(this.proxySwfName, 1, 1, '6,0,65,0');
    ft.addFlashVar('lcId', this.uid);
    ft.addFlashVar('functionName', args[0]);
    if (args.length > 1)
    {
    	var justArgs = new Array();
        for (var i = 1; i < args.length; ++i)
        {
            justArgs.push(args[i]);
        }
        ft.addFlashVars(this.flashSerializer.serialize(justArgs));
    }

	
    var divName = '_flash_proxy_' + this.uid;
    if(!document.getElementById(divName))
    {
        var newTarget = document.createElement("div");
        newTarget.id = divName;
        document.body.appendChild(newTarget);
    }
	var target = document.getElementById(divName);
	target.innerHTML = ft.toString();
}

/**
 * This is the function that proxies function calls from Flash to JavaScript.
 * It is called implicitly, so you won't ever need to call it.
 */
FlashProxy.callJS = function(command, args)
{
	var argsArray = eval(args);
	var scope = FlashProxy.fpmap[argsArray.shift()].callbackScope;

    if(scope && (command.indexOf('.') < 0))
	{
		var functionToCall = scope[command];
		functionToCall.apply(scope, argsArray);
	}
	else
	{
    	var functionToCall = eval(command);
		functionToCall.apply(functionToCall, argsArray);
	}
}

/**
 * This function gets called when a Flash function call is complete. It checks the
 * queue and figures out whether there is another call to make.
 */
FlashProxy.callComplete = function(uid)
{
	var fp = FlashProxy.fpmap[uid];
	if (fp != null)
	{
		fp.q.shift();
		if (fp.q.length > 0)
		{
			fp._execute(fp.q[0]);
		}
	}
}

FlashProxy.fpmap = new Object();

/*
Macromedia(r) Flash(r) JavaScript Integration Kit License


Copyright (c) 2005 Macromedia, inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. The end-user documentation included with the redistribution, if any, must
include the following acknowledgment:

"This product includes software developed by Macromedia, Inc.
(http://www.macromedia.com)."

Alternately, this acknowledgment may appear in the software itself, if and
wherever such third-party acknowledgments normally appear.

4. The name Macromedia must not be used to endorse or promote products derived
from this software without prior written permission. For written permission,
please contact devrelations@macromedia.com.

5. Products derived from this software may not be called "Macromedia" or
"Macromedia Flash", nor may "Macromedia" or "Macromedia Flash" appear in their
name.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MACROMEDIA OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

--

This code is part of the Flash / JavaScript Integration Kit:
http://www.macromedia.com/go/flashjavascript/

Created by:

Christian Cantrell
http://weblogs.macromedia.com/cantrell/
mailto:cantrell@macromedia.com

Mike Chambers
http://weblogs.macromedia.com/mesh/
mailto:mesh@macromedia.com

Macromedia
*/

/**
 * The FlashSerializer serializes JavaScript variables of types object, array, string,
 * number, date, boolean, null or undefined into XML. 
 */

/**
 * Create a new instance of the FlashSerializer.
 * useCdata: Whether strings should be treated as character data. If false, strings are simply XML encoded.
 */
function FlashSerializer(useCdata)
{
    this.useCdata = useCdata;
}

/**
 * Serialize an array into a format that can be deserialized in Flash. Supported data types are object,
 * array, string, number, date, boolean, null, and undefined. Returns a string of serialized data.
 */
FlashSerializer.prototype.serialize = function(args)
{
    var qs = new String();

    for (var i = 0; i < args.length; ++i)
    {
        switch(typeof(args[i].valueOf()))
        {
            case 'undefined':
                qs += 't'+(i)+'=undf';
                break;
            case 'string':
                qs += 't'+(i)+'=str&d'+(i)+'='+encodeURL(args[i]);
                break;
            case 'number':
                qs += 't'+(i)+'=num&d'+(i)+'='+encodeURL(args[i]);
                break;
            case 'boolean':
                qs += 't'+(i)+'=bool&d'+(i)+'='+encodeURL(args[i]);
                break;
            case 'object':
                if (args[i] == null)
                {
                    qs += 't'+(i)+'=null';
                }
                else if (args[i] instanceof Date)
                {
                    qs += 't'+(i)+'=date&d'+(i)+'='+encodeURL(args[i].getTime());
                }
                else // array or object
                {
                    try
                    {
                        qs += 't'+(i)+'=xser&d'+(i)+'='+encodeURL(this._serializeXML(args[i]));
                    }
                    catch (exception)
                    {
                        throw new Exception("FlashSerializationException",
                                            "The following error occurred during complex object serialization: " + exception.getMessage());
                    }
                }
                break;
            default:
                throw new Exception("FlashSerializationException",
                                    "You can only serialize strings, numbers, booleans, dates, objects, arrays, nulls, and undefined.");
        }

        if (i != (args.length - 1))
        {
            qs += '&';
        }
    }

    return qs;
}

/**
 * Private
 */
FlashSerializer.prototype._serializeXML = function(obj)
{
    var doc = new Object();
    doc.xml = '<fp>'; 
    try
    {
        this._serializeNode(obj, doc, null);
    }
    catch (exception)
    {
        if (exception.message)
        {
            throw new Exception("FlashSerializationException",
                                "Unable to serialize object because: " + exception.message);
        }
        throw exception;
    }
    doc.xml += '</fp>'; 
    return doc.xml;
}

/**
 * Private
 */
FlashSerializer.prototype._serializeNode = function(obj, doc, name)
{
    switch(typeof(obj))
    {
        case 'undefined':
            doc.xml += '<undf'+this._addName(name)+'/>';
            break;
        case 'string':
            doc.xml += '<str'+this._addName(name)+'>'+this._escapeXml(obj)+'</str>';
            break;
        case 'number':
            doc.xml += '<num'+this._addName(name)+'>'+obj+'</num>';
            break;
        case 'boolean':
            doc.xml += '<bool'+this._addName(name)+' val="'+obj+'"/>';
            break;
        case 'object':
            if (obj == null)
            {
                doc.xml += '<null'+this._addName(name)+'/>';
            }
            else if (obj instanceof Date)
            {
                doc.xml += '<date'+this._addName(name)+'>'+obj.getTime()+'</date>';
            }
            else if (obj instanceof Array)
            {
                doc.xml += '<array'+this._addName(name)+'>';
                for (var i = 0; i < obj.length; ++i)
                {
                    this._serializeNode(obj[i], doc, null);
                }
                doc.xml += '</array>';
            }
            else
            {
                doc.xml += '<obj'+this._addName(name)+'>';
                for (var n in obj)
                {
                    if (typeof(obj[n]) == 'function')
                        continue;
                    this._serializeNode(obj[n], doc, n);
                }
                doc.xml += '</obj>';
            }
            break;
        default:
            throw new Exception("FlashSerializationException",
                                "You can only serialize strings, numbers, booleans, objects, dates, arrays, nulls and undefined");
            break;
    }
}

/**
 * Private
 */
FlashSerializer.prototype._addName= function(name)
{
    if (name != null)
    {
        return ' name="'+name+'"';
    }
    return '';
}

/**
 * Private
 */
FlashSerializer.prototype._escapeXml = function(str)
{
    if (this.useCdata)
        return '<![CDATA['+str+']]>';
    else
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;');
}

/*
Macromedia(r) Flash(r) JavaScript Integration Kit License


Copyright (c) 2005 Macromedia, inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. The end-user documentation included with the redistribution, if any, must
include the following acknowledgment:

"This product includes software developed by Macromedia, Inc.
(http://www.macromedia.com)."

Alternately, this acknowledgment may appear in the software itself, if and
wherever such third-party acknowledgments normally appear.

4. The name Macromedia must not be used to endorse or promote products derived
from this software without prior written permission. For written permission,
please contact devrelations@macromedia.com.

5. Products derived from this software may not be called "Macromedia" or
"Macromedia Flash", nor may "Macromedia" or "Macromedia Flash" appear in their
name.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MACROMEDIA OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

--

This code is part of the Flash / JavaScript Integration Kit:
http://www.macromedia.com/go/flashjavascript/

Created by:

Christian Cantrell
http://weblogs.macromedia.com/cantrell/
mailto:cantrell@macromedia.com

Mike Chambers
http://weblogs.macromedia.com/mesh/
mailto:mesh@macromedia.com

Macromedia
*/

/**
 * Generates a browser-specific Flash tag. Create a new instance, set whatever
 * properties you need, then call either toString() to get the tag as a string, or
 * call write() to write the tag out.
 *
 * The properties src, width, height and version are required when creating a new
 * instance of the FlashTag, but there are setters to let you change them, as well.
 * That way, if you want to render more than one piece of Flash content, you can do
 * so without creating a new instance of the tag.
 *
 * For more information on supported parameters, see:
 * http://www.macromedia.com/cfusion/knowledgebase/index.cfm?id=tn_12701
 */


/**
 * Creates a new instance of the FlashTag.
 * src: The path to the SWF file.
 * width: The width of your Flash content.
 * height: the height of your Flash content.
 * version: the required version of the Flash Player for the specified content.
 *
 * These are the only 4 properites that are required.
 */
function FlashTag(src, width, height, version)
{
    if (arguments.length < 4)
    {
        throw new Exception('RequiredParameterException',
                            'You must pass in a src, width, height, and version when creating a FlashTag.');
    }

    // Required
    this.src            =  src;
    this.width          =  width;
    this.height         =  height;
    this.version        =  version;

    this.id             =  null;
    this.flashVars      =  null;
    this.flashVarsStr   =  null;
    this.genericParam   = new Object();
    this.ie = (navigator.appName.indexOf ("Microsoft") != -1) ? 1 : 0;
}

/**
 * Specifies the location (URL) of the Flash content to be loaded.
 */
FlashTag.prototype.setSource = function(src)
{
    this.src = src; 
}

/**
 * Specifies the width of the Flash content in either pixels or percentage of browser window. 
 */
FlashTag.prototype.setWidth = function(w)
{
    this.width = width; 
}

/**
 * Specifies the height of the Flash content in either pixels or percentage of browser window. 
 */
FlashTag.prototype.setHeight = function(h)
{
    this.h = height; 
}

/**
 * The required version of the Flash Player for the specified content. 
 */
FlashTag.prototype.setVersion = function(v)
{
    this.version = v;
}

/**
 * Identifies the Flash content to the host environment (a web browser, for example) so that
 * it can be referenced using a scripting language. This value will be used for both the 'id'
 * and 'name' attributes depending on the client platform and whether the object or the embed
 * tag are used.
 */
FlashTag.prototype.setId = function(id)
{
    this.id = id;
}

/**
 * Specifies the background color of the Flash content. Use this attribute to override the background
 * color setting specified in the Flash file. This attribute does not affect the background
 * color of the HTML page. 
 */
FlashTag.prototype.setBgcolor = function(bgc)
{
    if (bgc.charAt(0) != '#')
    {
        bgc = '#' + bgc;
    }
    this.genericParam['bgcolor'] = bgc;
}

/**
 * Allows you to set multiple Flash vars at once rather than adding them one at a time. The string
 * you pass in should contain all your Flash vars, properly URL encoded. This function can be used in
 * conjunction with addFlashVar.
 */
FlashTag.prototype.addFlashVars = function(fvs)
{
    this.flashVarsStr = fvs;
}

/**
 * Used to send root level variables to the Flash content. You can add as many name/value pairs as
 * you want. The formatting of the Flash vars (turning them into a query string) is handled automatically.
 */
FlashTag.prototype.addFlashVar = function(n, v)
{
    if (this.flashVars == null)
    {
        this.flashVars = new Object();
    }

    this.flashVars[n] = v;
}

/**
 * Used to remove Flash vars. This is primarily useful if you want to reuse an instance of the FlashTag
 * but you don't want to send the same variables to more than one piece of Flash content. 
 */
FlashTag.prototype.removeFlashVar = function(n)
{
    if (this.flashVars != null)
    {
        this.flashVars[n] = null;
    }
}

/**
 * (true, false) Specifies whether the browser should start Java when loading the Flash Player for the first time.
 * The default value is false if this property is not set. 
 */
FlashTag.prototype.setSwliveconnect = function(swlc)
{
    this.genericParam['swliveconnect'] = swlc;
}

/**
 * (true, false) Specifies whether the Flash content begins playing immediately on loading in the browser.
 * The default value is true if this property is not set. 
 */
FlashTag.prototype.setPlay = function(p)
{
    this.genericParam['play'] = p;
}

/**
 * (true, false) Specifies whether the Flash content repeats indefinitely or stops when it reaches the last frame.
 * The default value is true if this property is not set. 
 */
FlashTag.prototype.setLoop = function(l)
{
    this.genericParam['loop'] = l;
}

/**
 * (true,false) Whether or not to display the full Flash menu. If false, displays a menu that contains only
 * the Settings and the About Flash options. 
 */
FlashTag.prototype.setMenu = function(m)
{
    this.genericParam['menu'] = m;
}

/**
 * (low, high, autolow, autohigh, best) Sets the quality at which the Flash content plays.
 */
FlashTag.prototype.setQuality = function(q)
{
    if (q != 'low' && q != 'high' && q != 'autolow' && q != 'autohigh' && q != 'best')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "low", "high", "autolow", "autohigh", and "best".');
    }
    this.genericParam['quality'] = q;
}

/**
 * (showall, noborder, exactfit) Determins how the Flash content scales.
 */
FlashTag.prototype.setScale = function(sc)
{
    if (sc != 'showall' && sc != 'noborder' && sc != 'exactfit')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "showall", "noborder", and "exactfit".');
    }
    this.genericParam['scale'] = sc;
}

/**
 * (l, t, r, b) Align the Flash content along the corresponding edge of the browser window and crop
 * the remaining three sides as needed.
 */
FlashTag.prototype.setAlign= function(a)
{
    if (a != 'l' && a != 't' && a != 'r' && a != 'b')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "l", "t", "r" and "b".');
    }
    this.genericParam['align'] = a;
}

/**
 * (l, t, r, b, tl, tr, bl, br) Align the Flash content along the corresponding edge of the browser
 * window and crop the remaining three sides as needed.
 */
FlashTag.prototype.setSalign= function(sa)
{
    if (sa != 'l' && sa != 't' && sa != 'r' && sa != 'b' && sa != 'tl' && sa != 'tr' && sa != 'bl' && sa != 'br')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "l", "t", "r", "b", "tl", "tr", "bl" and "br".');
    }
    this.genericParam['salign'] = sa;
}

/**
 * (window, opaque, transparent) Sets the Window Mode property of the Flash content for transparency,
 * layering, and positioning in the browser. 
 */
FlashTag.prototype.setWmode = function(wm)
{
    if (wm != 'window' && wm != 'opaque' && wm != 'transparent')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "window", "opaque", and "transparent".');
    }
    this.genericParam['wmode'] = wm;
}

/**
 * Specifies the base directory or URL used to resolve all relative path statements in your Flash content.
 */
FlashTag.prototype.setBase = function(base)
{
    this.genericParam['base'] = base;
}

/**
 * (never, always) Controls the ability to perform outbound scripting from within Flash content. 
 */
FlashTag.prototype.setAllowScriptAccess = function(sa)
{
    if (sa != 'never' && sa != 'always')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "never" and "always".');
    }
    this.genericParam['allowScriptAccess'] = sa;
}

/**
 * Get the Flash tag as a string. 
 */
FlashTag.prototype.toString = function()
{
    var flashTag = new String();
    if (this.ie)
    {
        flashTag += '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" ';
        if (this.id != null)
        {
            flashTag += 'id="'+this.id+'" ';
        }
        flashTag += 'codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version='+this.version+'" ';
        flashTag += 'width="'+this.width+'" ';
        flashTag += 'height="'+this.height+'">';
        flashTag += '<param name="movie" value="'+this.src+'"/>';

        for (var n in this.genericParam)
        {
            if (this.genericParam[n] != null)
            {
                flashTag += '<param name="'+n+'" value="'+this.genericParam[n]+'"/>';
            }
        }

        if (this.flashVars != null)
        {
            var fv = this.getFlashVarsAsString();
            if (fv.length > 0)
            {
                flashTag += '<param name="flashvars" value="'+fv+'"/>';
            }
        }
        flashTag += '</object>';
    }
    else
    {
        flashTag += '<embed src="'+this.src+'"';
        flashTag += ' width="'+this.width+'"';
        flashTag += ' height="'+this.height+'"';
        flashTag += ' type="application/x-shockwave-flash"';
        if (this.id != null)
        {
            flashTag += ' name="'+this.id+'"';
            flashTag += ' id="'+this.id+'"';
        }

        for (var n in this.genericParam)
        {
            if (this.genericParam[n] != null)
            {
                flashTag += (' '+n+'="'+this.genericParam[n]+'"');
            }
        }

        if (this.flashVars != null)
        {
            var fv = this.getFlashVarsAsString();
            if (fv.length > 0)
            {
                flashTag += ' flashvars="'+fv+'"';
            }
        }
        flashTag += ' pluginspage="http://www.macromedia.com/go/getflashplayer">';
        flashTag += '</embed>';
    }
    return flashTag;
}

/**
 * Write the Flash tag out. Pass in a reference to the document to write to. 
 */
FlashTag.prototype.write = function(doc)
{
	if (doc.write)
    	doc.write(this.toString());
    else
    	doc.innerHTML = this.toString();
}

/**
 * Write the Flash tag out. Pass in a reference to the document to write to. 
 */
FlashTag.prototype.getFlashVarsAsString = function()
{
    var qs = new String();
    for (var n in this.flashVars)
    {
        if (this.flashVars[n] != null)
        {
            qs += (encodeURL(n)+'='+encodeURL(this.flashVars[n])+'&');
        }
    }

    if (this.flashVarsStr != null)
    {
        return qs + this.flashVarsStr;
    }

    return qs.substring(0, qs.length-1);
}

/*  Function Equivalent to java.net.URLEncoder.encode(String, "UTF-8")

	published at http://www.cresc.co.jp/tech/java/URLencoding/JavaScript_URLEncoding.htm
    
    Copyright (C) 2002, Cresc Corp.

    Version: 1.0

*/
function encodeURL(str) {
	str = str.toString();
    var s0, i, s, u;
    s0 = "";                // encoded str
    for (i = 0; i < str.length; i++){   // scan the source
        s = str.charAt(i);
        u = str.charCodeAt(i);          // get unicode of the char
        if (s == " ") {
        	s0 += "+";
        }       // SP should be converted to "+"
        else {
            if ( u == 0x2a || u == 0x2d || u == 0x2e || u == 0x5f || 
            	((u >= 0x30) && (u <= 0x39)) || 
            	((u >= 0x41) && (u <= 0x5a)) || 
            	((u >= 0x61) && (u <= 0x7a)))  {       // check for escape
                s0 = s0 + s;            // don't escape
            }
            else {                  // escape
                if ((u >= 0x0) && (u <= 0x7f)){     // single byte format
                    s = "0"+u.toString(16);
                    s0 += "%"+ s.substr(s.length-2);
                }
                else if (u > 0x1fffff){     // quaternary byte format (extended)
                    s0 += "%" + (oxf0 + ((u & 0x1c0000) >> 18)).toString(16);
                    s0 += "%" + (0x80 + ((u & 0x3f000) >> 12)).toString(16);
                    s0 += "%" + (0x80 + ((u & 0xfc0) >> 6)).toString(16);
                    s0 += "%" + (0x80 + (u & 0x3f)).toString(16);
                }
                else if (u > 0x7ff){        // triple byte format
                    s0 += "%" + (0xe0 + ((u & 0xf000) >> 12)).toString(16);
                    s0 += "%" + (0x80 + ((u & 0xfc0) >> 6)).toString(16);
                    s0 += "%" + (0x80 + (u & 0x3f)).toString(16);
                }
                else {                      // double byte format
                    s0 += "%" + (0xc0 + ((u & 0x7c0) >> 6)).toString(16);
                    s0 += "%" + (0x80 + (u & 0x3f)).toString(16);
                }
            }
        }
    }
    return s0;
}

 
 
 

/*  Function Equivalent to java.net.URLDecoder.decode(String, "UTF-8")

	published at http://www.cresc.co.jp/tech/java/URLencoding/JavaScript_URLEncoding.htm
	
    Copyright (C) 2002, Cresc Corp.

    Version: 1.0

*/

function decodeURL(str) {
    var s0, i, j, s, ss, u, n, f;
    s0 = "";                // decoded str
    for (i = 0; i < str.length; i++) {   // scan the source str
        s = str.charAt(i);
        if (s == "+") {
        	s0 += " ";
        }       // "+" should be changed to SP
        else {
            if (s != "%"){
            	s0 += s;
            }     // add an unescaped char
            else{               // escape sequence decoding
                u = 0;          // unicode of the character
                f = 1;          // escape flag, zero means end of this sequence
                while (true) {
                    ss = "";        // local str to parse as int
                    for (j = 0; j < 2; j++ ) {  // get two maximum hex characters for parse
                        sss = str.charAt(++i);
                        if (((sss >= "0") && (sss <= "9")) || 
                        	((sss >= "a") && (sss <= "f")) || 
                        	((sss >= "A") && (sss <= "F")))  {
                                ss += sss;      // if hex, add the hex character
                            } 
                            else {
                                --i; 
                                break;
                            }    // not a hex char., exit the loop
                        }
                    n = parseInt(ss, 16);           // parse the hex str as byte
                    if (n <= 0x7f)                  {u = n; f = 1;}   // single byte format
                    if ((n >= 0xc0) && (n <= 0xdf)) {u = n & 0x1f; f = 2;}   // double byte format
                    if ((n >= 0xe0) && (n <= 0xef)) {u = n & 0x0f; f = 3;}   // triple byte format
                    if ((n >= 0xf0) && (n <= 0xf7)) {u = n & 0x07; f = 4;}   // quaternary byte format (extended)
                    if ((n >= 0x80) && (n <= 0xbf)) {u = (u << 6) + (n & 0x3f); --f;} // not a first, shift and add 6 lower bits
                    if (f <= 1){break;}         // end of the utf byte sequence
                    if (str.charAt(i + 1) == "%"){ i++ ;} // test for the next shift byte
                    else {break;}                   // abnormal, format error
                }
            s0 += String.fromCharCode(u);           // add the escaped character
            }
        }
    }
    return s0;

}


if(window.jsloaded) {jsloaded('/statics/Flash.js')}

