# -*- encoding: utf-8 -*-
#
# Copyright (c) 2007-2008 The PyAMF Project.
# See LICENSE for details.

"""
AMF0 implementation.

C{AMF0} supports the basic data types used for the NetConnection, NetStream,
LocalConnection, SharedObjects and other classes in the Flash Player.

@see: U{AMF documentation on OSFlash (external)
<http://osflash.org/documentation/amf>}

@author: U{Arnar Birgisson<mailto:arnarbi@gmail.com>}
@author: U{Thijs Triemstra<mailto:info@collab.nl>}
@author: U{Nick Joyce<mailto:nick@boxdesign.co.uk>}

@since: 0.1.0
"""

import datetime, types

import pyamf
from pyamf import util

class ASTypes:
    """
    All AMF0 data types used in ActionScript 1.0 and 2.0.

    @see: U{Data types on OSFlash (external)
    <http://osflash.org/documentation/amf/astypes>}
    """
    #: Represented as 9 bytes: 1 byte for C{0×00} and 8 bytes a double
    #: representing the value of the number.
    NUMBER      = 0x00
    #: Represented as 2 bytes: 1 byte for C{0×01} and a second, C{0×00}
    #: for C{False}, C{0×01} for C{True}.
    BOOL        = 0x01
    #: Represented as 3 bytes + len(String): 1 byte C{0×02}, then a UTF8 string,
    #: including the top two bytes representing string length as a C{int}.
    STRING      = 0x02
    #: Represented as 1 byte, C{0×03}, then pairs of UTF8 string, the key, and
    #: an AMF element, ended by three bytes, C{0×00} C{0×00} C{0×09}.
    OBJECT      = 0x03
    #: MovieClip does not seem to be supported by Remoting.
    #: It may be used by other AMF clients such as SharedObjects.
    MOVIECLIP   = 0x04
    #: 1 single byte, C{0×05} indicates null.
    NULL        = 0x05
    #: 1 single byte, C{0×06} indicates null.
    UNDEFINED   = 0x06
    #: When an ActionScript object refers to itself, such C{this.self = this}, or
    #: when objects are repeated within the same scope (for example, as the two
    #: parameters of the same function called), a code of C{0×07} and an C{int},
    #: the reference number, are written.
    REFERENCE   = 0x07
    #: A MixedArray is indicated by code C{0×08}, then a Long representing the
    #: highest numeric index in the array, or 0 if there are none or they are all
    #: negative. After that follow the elements in key : value pairs.
    MIXEDARRAY  = 0x08
    #: @see: L{OBJECT}
    OBJECTTERM  = 0x09
    #: An array is indicated by C{0x0A}, then a Long for array length, then the
    #: array elements themselves. Arrays are always sparse; values for inexistant
    #: keys are set to null (C{0×06}) to maintain sparsity.
    ARRAY       = 0x0a
    #: Date is represented as C{00x0B}, then a double, then an C{int}. The double
    #: represents the number of milliseconds since 01/01/1970. The C{int} represents
    #: the timezone offset in minutes between GMT. Note for the latter than values
    #: greater than 720 (12 hours) are represented as M{2^16} - the value. Thus GMT+1
    #: is 60 while GMT-5 is 65236.
    DATE        = 0x0b
    #: LongString is reserved for strings larger then M{2^16} characters long. It
    #: is represented as C{00x0C} then a LongUTF.
    LONGSTRING  = 0x0c
    #: Trying to send values which don’t make sense, such as prototypes, functions,
    #: built-in objects, etc. will be indicated by a single C{00x0D} byte.
    UNSUPPORTED = 0x0d
    #: Remoting Server -> Client only.
    #: @see: L{RecordSet}
    #: @see: U{RecordSet structure on OSFlash (external)
    #: <http://osflash.org/documentation/amf/recordset>}
    RECORDSET   = 0x0e
    #: The XML element is indicated by C{00x0F} and followed by a LongUTF containing
    #: the string representation of the XML object. The receiving gateway may which
    #: to wrap this string inside a language-specific standard XML object, or simply
    #: pass as a string.
    XML         = 0x0f
    #: A typed object is indicated by C{0×10}, then a UTF string indicating class
    #: name, and then the same structure as a normal C{0×03} Object. The receiving
    #: gateway may use a mapping scheme, or send back as a vanilla object or
    #: associative array.
    TYPEDOBJECT = 0x10
    #: An AMF message sent from an AS3 client such as the Flash Player 9 may break
    #: out into L{AMF3<pyamf.amf3>} mode. In this case the next byte will be the
    #: AMF3 type code and the data will be in AMF3 format until the decoded object
    #: reaches it’s logical conclusion (for example, an object has no more keys).
    AMF3        = 0x11

#: List of available ActionScript types in AMF0.
ACTIONSCRIPT_TYPES = []

for x in ASTypes.__dict__:
    if not x.startswith('_'):
        ACTIONSCRIPT_TYPES.append(ASTypes.__dict__[x])
del x

class Context(pyamf.BaseContext):
    """
    I hold the AMF0 context for en/decoding streams.

    AMF0 object references start at index 1.
    """

    def clear(self):
        """
        Resets the context.

        The C{amf3_objs} var keeps a list of objects that were encoded
        in L{AMF3<pyamf.amf3>}.
        """
        pyamf.BaseContext.clear(self)

        self.amf3_objs = []
        self.rev_amf3_objs = {}

    def _getObject(self, ref):
        return self.objects[ref + 1]

    def __copy__(self):
        """
        @rtype:
        @return:
        """
        copy = self.__class__()
        copy.amf3_objs = self.amf3_objs
        copy.rev_amf3_objs = self.rev_amf3_objs

        return copy

    def getAMF3ObjectReference(self, obj):
        """
        Gets a reference for an object.

        @type obj:
        @param obj:
        @raise ReferenceError: Object reference could not be found.

        @rtype:
        @return:
        """
        try:
            return self.rev_amf3_objs[id(obj)]
        except KeyError:
            raise ReferenceError

    def addAMF3Object(self, obj):
        """
        Adds an AMF3 reference to C{obj}.

        @type obj: mixed
        @param obj: The object to add to the context.

        @rtype: int
        @return: Reference to C{obj}.
        """
        self.amf3_objs.append(obj)
        idx = len(self.amf3_objs) - 1
        self.rev_amf3_objs[id(obj)] = idx

        return idx

class Decoder(pyamf.BaseDecoder):
    """
    Decodes an AMF0 stream.
    """

    context_class = Context
    # XXX nick: Do we need to support ASTypes.MOVIECLIP here?
    type_map = {
        ASTypes.NUMBER:     'readNumber',
        ASTypes.BOOL:       'readBoolean',
        ASTypes.STRING:     'readString',
        ASTypes.OBJECT:     'readObject',
        ASTypes.NULL:       'readNull',
        ASTypes.UNDEFINED:  'readUndefined',
        ASTypes.REFERENCE:  'readReference',
        ASTypes.MIXEDARRAY: 'readMixedArray',
        ASTypes.ARRAY:      'readList',
        ASTypes.DATE:       'readDate',
        ASTypes.LONGSTRING: 'readLongString',
        # TODO: do we need a special value here?
        ASTypes.UNSUPPORTED:'readNull',
        ASTypes.XML:        'readXML',
        ASTypes.TYPEDOBJECT:'readTypedObject',
        ASTypes.AMF3:       'readAMF3'
    }

    def readType(self):
        """
        Read and returns the next byte in the stream and determine its type.

        @raise DecodeError: AMF0 type not recognized.
        @return: AMF0 type.
        """
        type = self.stream.read_uchar()

        if type not in ACTIONSCRIPT_TYPES:
            raise pyamf.DecodeError("Unknown AMF0 type 0x%02x at %d" % (
                type, self.stream.tell() - 1))

        return type

    def readNumber(self):
        """
        Reads a Number.

        In ActionScript 1 and 2 the NumberASTypes type represents all numbers,
        both floats and integers.

        @rtype: C{int}
        @return: Number
        """
        return self.stream.read_double()

    def readBoolean(self):
        """
        Reads a Boolean.

        @rtype: C{bool}
        @return: Boolean.
        """
        return bool(self.stream.read_uchar())

    def readNull(self):
        """
        Reads null.

        @return: C{None}
        @rtype: C{None}
        """
        return None

    def readUndefined(self):
        """
        Reads an undefined value.

        @return: L{pyamf.Undefined}
        """
        return pyamf.Undefined

    def readMixedArray(self):
        """
        Read mixed array.

        @rtype: C{dict}
        @return: C{dict} read from the stream
        """
        len = self.stream.read_ulong()
        obj = {}
        self.context.addObject(obj)
        self._readObject(obj)
        ikeys = []

        for key in obj.keys():
            try:
                ikey = int(key)
                ikeys.append((key, ikey))
                obj[ikey] = obj[key]
                del obj[key]
            except ValueError:
                # XXX: do we want to ignore this?
                pass

        ikeys.sort()

        return obj

    def readList(self):
        """
        Read a list from the data stream.

        @rtype: C{list}
        @return: C{list}
        """
        obj = []
        self.context.addObject(obj)
        len = self.stream.read_ulong()

        for i in xrange(len):
            obj.append(self.readElement())

        return obj

    def readTypedObject(self):
        """
        Reads an object from the stream and attempts to 'cast' it.

        @rtype:
        @return:

        @see: L{load_class<pyamf.load_class>}
        """
        classname = self.readString()
        klass = pyamf.load_class(classname)

        ret = klass()
        self.context.addObject(ret)
        self._readObject(ret)

        return ret

    def readAMF3(self):
        """
        Read AMF3 elements from the data stream.

        @rtype: C{mixed}
        @return: The AMF3 element read from the stream
        """
        decoder = pyamf._get_decoder_class(pyamf.AMF3)(self.stream)

        element = decoder.readElement()
        self.context.addAMF3Object(element)

        return element

    def readString(self):
        """
        Reads a string from the data stream.

        @rtype: C{str}
        @return:
        """
        len = self.stream.read_ushort()
        return self.stream.read_utf8_string(len)

    def _readObject(self, obj):
        key = self.readString()

        ot = chr(ASTypes.OBJECTTERM)

        while self.stream.peek() != ot:
            if isinstance(obj, (list, dict, tuple)):
                obj[key] = self.readElement()
            else:
                value = self.readElement()

                try:
                    setattr(obj, key, value)
                except AttributeError:
                    obj.__dict__[key] = value

            key = self.readString()

        # discard the end marker (ASTypes.OBJECTTERM)
        self.stream.read(len(ot))

    def readObject(self):
        """
        Reads an object from the data stream.

        @return: The object
        @rtype: L{pyamf.Bag}
        """
        obj = pyamf.Bag()
        self.context.addObject(obj)

        self._readObject(obj)

        return obj

    def readReference(self):
        """
        Reads a reference from the data stream.

        @rtype:
        @return:
        """
        idx = self.stream.read_ushort()

        return self.context.getObject(idx)

    def readDate(self):
        """
        Reads a UTC date from the data stream.

        Date: C{0x0B T7 T6} .. C{T0 Z1 Z2 T7} to C{T0} form a 64 bit
        Big Endian number that specifies the number of nanoseconds
        that have passed since 1/1/1970 0:00 to the specified time.
        This format is UTC 1970. C{Z1} and C{Z0} for a 16 bit Big
        Endian number indicating the indicated time's timezone in
        minutes.

        @rtype:
        @return:
        """
        ms = self.stream.read_double() / 1000.0
        tz = self.stream.read_short()

        # Timezones are ignored
        d = datetime.datetime.utcfromtimestamp(ms)
        self.context.addObject(d)

        return d

    def readLongString(self):
        """
        Read UTF8 string.

        @rtype:
        @return:
        """
        len = self.stream.read_ulong()

        return self.stream.read_utf8_string(len)

    def readXML(self):
        """
        Read XML.

        @rtype:
        @return:
        """
        data = self.readLongString()
        xml = util.ET.fromstring(data)
        self.context.addObject(xml)

        return xml

class Encoder(pyamf.BaseEncoder):
    """
    Encodes an AMF0 stream.
    """

    context_class = Context
    type_map = [
        ((types.BuiltinFunctionType, types.BuiltinMethodType,),
            "writeUnsupported"),
        ((lambda x: x == pyamf.Undefined,), "writeUndefined"),
        ((bool,), "writeBoolean"),
        ((int,long,float), "writeNumber"),
        ((types.StringTypes,), "writeString"),
        ((util.ET.iselement,), "writeXML"),
        ((pyamf.Bag,), "writeObject"),
        ((types.DictType,), "writeMixedArray"),
        ((types.ListType,types.TupleType,), "writeArray"),
        ((datetime.date, datetime.datetime), "writeDate"),
        ((types.NoneType,), "writeNull"),
        ((types.InstanceType,types.ObjectType,), "writeObject"),
    ]

    def writeType(self, type):
        """
        Writes the type to the stream.

        @type   type: C{int}
        @param  type: ActionScript type.
        
        @raise EncodeError: AMF0 type is not recognized.
        """
        if type not in ACTIONSCRIPT_TYPES:
            raise pyamf.EncodeError("Unknown AMF0 type 0x%02x at %d" % (
                type, self.stream.tell() - 1))

        self.stream.write_uchar(type)

    def writeUndefined(self, data):
        """
        Writes the undefined data type to the stream.
        """
        self.writeType(ASTypes.UNDEFINED)

    def writeUnsupported(self, data):
        """
        Writes unsupported data type to the stream.

        @type   data:
        @param  data:
        """
        self.writeType(ASTypes.UNSUPPORTED)

    def _writeElementFunc(self, data):
        """
        Gets a function based on the type of data.

        @see: L{pyamf.BaseEncoder._writeElementFunc}
        """
        # There is a very specific use case that we must check for.
        # In the context there is an array of amf3_objs that contain references
        # to objects that are to be encoded in amf3
        try:
            self.context.getAMF3ObjectReference(data)
            return self.writeAMF3
        except ReferenceError:
            pass

        return pyamf.BaseEncoder._writeElementFunc(self, data)

    def writeElement(self, data):
        """
        Writes the data.

        @type   data: C{mixed}
        @param  data: The data to be encoded to the AMF0 data stream.

        @raise EncodeError: Unable to encode data.
        """
        func = self._writeElementFunc(data)

        if func is None:
            # XXX nick: Should we be generating a warning here?
            self.writeUnsupported(data)
        else:
            try:
                func(data)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                raise
                raise pyamf.EncodeError, "Unable to encode '%r'" % data

    def writeNull(self, n):
        """
        Write null type to data stream.

        @type   n: C{None}
        @param  n: Is ignored.
        """
        self.writeType(ASTypes.NULL)

    def writeArray(self, a):
        """
        Write array to the stream.

        @type   a: L{BufferedByteStream<pyamf.util.BufferedByteStream>}
        @param  a: AMF data.
        """
        try:
            self.writeReference(a)
            return
        except pyamf.ReferenceError:
            self.context.addObject(a)

        self.writeType(ASTypes.ARRAY)
        self.stream.write_ulong(len(a))

        for data in a:
            self.writeElement(data)

    def writeNumber(self, n):
        """
        Write number to data stream.

        @type   n: L{BufferedByteStream}
        @param  n: AMF data.
        """
        self.writeType(ASTypes.NUMBER)
        self.stream.write_double(float(n))

    def writeBoolean(self, b):
        """
        Write boolean to data stream.

        @type   b: L{BufferedByteStream}
        @param  b: AMF data.
        """
        self.writeType(ASTypes.BOOL)

        if b:
            self.stream.write_uchar(1)
        else:
            self.stream.write_uchar(0)

    def writeString(self, s, writeType=True):
        """
        Write string to data stream.

        @type   s: L{BufferedByteStream}
        @param  s: AMF data.
        @type   writeType: C{bool}
        @param  writeType: Write data type.
        """
        if not isinstance(s, basestring):
            s = str(s)
 
        if not isinstance(s, unicode):
            s = unicode(s, errors='ignore')

        s = s.encode('utf8')

        if len(s) > 0xffff:
            if writeType:
                self.writeType(ASTypes.LONGSTRING)
            self.stream.write_ulong(len(s))
        else:
            if writeType:
                self.stream.write_uchar(ASTypes.STRING)
            self.stream.write_ushort(len(s))

        self.stream.write(s)

    def writeReference(self, o):
        """
        Write reference to data stream.

        @type   o: L{BufferedByteStream}
        @param  o: AMF data.
        """
        idx = self.context.getObjectReference(o)

        self.writeType(ASTypes.REFERENCE)
        self.stream.write_ushort(idx)

    def _writeDict(self, o):
        """
        Write C{dict} to data stream.

        @type   o: C{iterable}
        @param  o: AMF data.
        """
        for key, val in o.iteritems():
            self.writeString(key, False)
            self.writeElement(val)

    def writeMixedArray(self, o):
        """
        Write mixed array to data stream.

        @type   o: L{BufferedByteStream}
        @param  o: AMF data.
        """
        try:
            self.writeReference(o)
            return
        except pyamf.ReferenceError:
            self.context.addObject(o)

        self.writeType(ASTypes.MIXEDARRAY)

        # TODO: optimise this
        # work out the highest integer index
        try:
            # list comprehensions to save the day
            max_index = max([y[0] for y in o.items()
                if isinstance(y[0], (int, long))])

            if max_index < 0:
                max_index = 0
        except ValueError, e:
            max_index = 0

        self.stream.write_ulong(max_index)

        self._writeDict(o)
        self._writeEndObject()

    def _writeEndObject(self):
        # Write a null string, this is an optimisation so that we don't have to
        # wasting precious cycles by encoding the string etc.
        self.stream.write('\x00\x00')
        self.writeType(ASTypes.OBJECTTERM)

    def writeObject(self, o):
        """
        Write object to the stream.

        @type   o: L{BufferedByteStream}
        @param  o: AMF data.
        """
        try:
            self.writeReference(o)
            return
        except pyamf.ReferenceError:
            self.context.addObject(o)

        # Need to check here if this object has a registered alias
        try:
            alias = pyamf.get_class_alias(o)
        except pyamf.UnknownClassAlias:
            alias = None

        if alias is None:
            self.writeType(ASTypes.OBJECT)
        else:
            if 'amf3' in alias.metadata:
                self.writeAMF3(o)

                return

            if 'anonymous' in alias.metadata:
                self.writeType(ASTypes.OBJECT)
            else:
                self.writeType(ASTypes.TYPEDOBJECT)
                self.writeString(alias.alias, False)

        # TODO: give objects a chance of controlling what we send
        if alias is not None and alias.attrs is not None:
            it = alias.attrs
        elif hasattr(o, '__dict__'):
            it = o.__dict__.keys()
        else:
            # FIXME nick: Don't know how to represent the object here.
            it = []

        for key in it:
            self.writeString(key, False)
            self.writeElement(getattr(o, key))

        self._writeEndObject()

    def writeDate(self, d):
        """
        Writes a date to the data stream.

        @type   d: Instance of C{datetime.datetime}
        @param  d: The date to be written.
        """
        # According to the Red5 implementation of AMF0, dates references are
        # created, but not used
        secs = util.get_timestamp(d)
        tz = 0

        self.writeType(ASTypes.DATE)
        self.stream.write_double(secs * 1000.0)
        self.stream.write_short(tz)

    def writeXML(self, e):
        """
        Write XML to data stream.

        @type   e: L{BufferedByteStream}
        @param  e: AMF data.
        """
        data = util.ET.tostring(e, 'utf8')

        self.writeType(ASTypes.XML)
        self.stream.write_ulong(len(data))
        self.stream.write(data)

    def writeAMF3(self, data):
        """
        Writes an element to the datastream in L{AMF3<pyamf.amf3>} format.

        @type data: C{mixed}
        @param data: The data to be encoded.
        """
        encoder = pyamf._get_encoder_class(pyamf.AMF3)(self.stream)

        self.writeType(ASTypes.AMF3)
        encoder.writeElement(data)

def decode(stream, context=None):
    """
    A helper function to decode an AMF0 datastream.

    @type   stream: L{BufferedByteStream}
    @param  stream: AMF0 datastream.
    @type   context: L{Context<pyamf.amf0.Context>}
    @param  context: AMF0 Context.
    """
    decoder = Decoder(stream, context)

    for el in decoder.readElement():
        yield el

def encode(element, context=None):
    """
    A helper function to encode an element into AMF0 format.

    @type   element: C{mixed}
    @param  element: The element to encode
    @type   context: L{Context<pyamf.amf0.Context>}
    @param  context: AMF0 C{Context} to use for the encoding. This holds previously
        referenced objects etc.
    @rtype: C{StringIO}
    @return: The encoded stream.
    """
    buf = util.BufferedByteStream()
    encoder = Encoder(buf, context)

    encoder.writeElement(element)

    return buf

class RecordSet(object):
    """
    I represent the RecordSet class used in Flash
    Remoting to hold (amongst other things) SQL records.

    @ivar columns: The columns to send.
    @type columns: List of strings.
    @ivar items: The recordset data.
    @type items: List of lists, the order of the data corresponds
        to the order of the columns.
    @ivar service: Service linked to the recordset.
    @type service: 
    @ivar id: The id of the recordset.
    @type id: C{str}

    @see: U{RecordSet on OSFlash (external)
    <http://osflash.org/documentation/amf/recordset>}
    """

    def __init__(self, columns=[], items=[], service=None, id=None):
        self.columns = columns
        self.items = items
        self.service = service
        self.id = id

    def _get_server_info(self):
        ret = dict(totalCount=len(self.items), cursor=1, version=1,
            initialData=self.items, columnNames=self.columns)

        if self.service is not None:
            ret.update(serviceName=str(self.service.name))

        if self.id is not None:
            ret.update(id=str(self.id))

        return ret

    def _set_server_info(self, val):
        self.columns = val['columnNames']
        self.items = val['initialData']

        try:
            # TODO nick: find relevant service and link in here.
            self.service = pyamf.Bag({'name': val['serviceName']})
        except KeyError:
            self.service = None

        try:
            self.id = val['id']
        except KeyError:
            self.id = None

    serverInfo = property(_get_server_info, _set_server_info)

pyamf.register_class(RecordSet, 'RecordSet', attrs=['serverInfo'])
        