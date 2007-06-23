# vim: fileencoding=utf8
import amf
import datetime
import time
from types import *

class_mappings = {}
timeoffset = None

def get_module(mod_name):
    mod = __import__(mod_name)
    components = mod_name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def get_func(func_name):
    paths = func_name.split('.')
    mod_name = '.'.join(paths[0:-1])
    if not mod_name:
        mod_name = '__main__'
    mod = get_module(mod_name)
    func = getattr(mod, paths[-1], None)
    if callable(func):
        return func
    return None

def get_class(fqcn):
    try:
        mod_and_class = fqcn.split('.')
        if mod_and_class:
            mod_name = '.'.join(mod_and_class[:-1])
            class_name = mod_and_class[-1]
            #amf.logger.debug("get_class(%s) -- module='%s', class='%s'", fqcn, mod_name, class_name)
            mod = get_module(mod_name)
            clz = getattr(mod, class_name)
            if callable(clz):
                return clz
    except:
        pass

def classcast(type, obj={}):
    #amf.logger.debug("classcast(%s, %s)", str(type), str(obj))
    if class_mappings:
        type = class_mappings.get(type, type)
    clz = get_class(type)
    if clz:
        c = clz()
        for key, value in obj.iteritems():
            setattr(c, key, value)
        return c
    else:
        return obj

def get_as_type(obj):
    """Find the name of ActionScript class mapped to the class of given python object.
       If the mapping for the given object class is not found, return the class name of the object."""
    type = obj.__module__ + '.' + obj.__class__.__name__
    if class_mappings:
        for as_class, py_class in class_mappings.iteritems():
            if type == py_class:
                return as_class
    return type

def get_class_def(obj):
    class_name = get_as_type(obj)
    member_names = []
    for name in obj.__dict__.keys():
        member_names.append(name)
    class_def = {
            'type' : class_name,
            'externalizable' : False,
            'dynamic' : False,
            'num_of_members' : len(member_names),
            'member_names' : member_names,
            }
    return class_def


def to_binary(n):
    """Convert a decimal integer into its binary equivalent."""
    if isinstance(n, basestring):
        n = int(n)
    ret = ""
    if n > 1:
        ret = to_binary(n>>1)
    return ret + "01"[n&1]

def _custom_timeoffset_available():
    """Check if 'timeoffset' attribute is set or not."""
    return timeoffset is not None and isinstance(timeoffset, IntType)

def get_datetime_from_timestamp(ms):
    if _custom_timeoffset_available():
        class TZ(datetime.tzinfo):
            def utcoffset(self, dt):
                return datetime.timedelta(hours=timeoffset)
            def dst(self, dt):
                return datetime.timedelta(0)
            def tzname(self, dt):
                return ""
        tz = TZ()  
        return datetime.datetime.fromtimestamp(ms / 1000.0, tz) 
    return datetime.datetime.fromtimestamp(ms / 1000.0) 

def get_timestamp_from_date(date):
    timestamp = time.mktime(date.timetuple())
    if _custom_timeoffset_available():
        return (timestamp - timeoffset * 3600) * 1000
    return timestamp * 1000

        
