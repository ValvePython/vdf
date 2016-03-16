import sys 
from collections import Iterable

if sys.version_info[0] >= 3:
    string_type = str
    _iter_helper = lambda x: x
else:
    string_type = basestring
    _iter_helper = tuple
    

class VDFDict(dict):
    def __init__(self, values=None):
        """
        A dictionary implmentation which allows duplicate keys and contains the insert order.
        
    
        ``values`` can be used to initialize this `DuplicateOrderedDict` instance..
          Dict like objects and iterables containing iterables of the length 2 are supported. 
        """
        self.__omap = []
        if not values is None:
            self.update(values)
                
    def __repr__(self):
        out = "%s(" % self.__class__.__name__
        out += "%s)" % repr(self.items())
        return out
    
    def __len__(self):
        return len(self.__omap)
    
    def __setitem__(self, key, value):
        if not isinstance(key, tuple):
            idx = 0
            while True:
                if (idx, key) not in self:
                    self.__omap.append((idx, key))
                    break
                else:
                    idx += 1
            key = (idx, key)
        else:
            if key not in self:
                raise KeyError("%s doesn\'t exist" % repr(key))
        if not isinstance(key[1], string_type):
            raise TypeError("The key need to be a string")      
        super(VDFDict, self).__setitem__(key, value)
        
    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (0, key)
        return super(VDFDict, self).__getitem__(key)
    
    def __delitem__(self, key):
        if not isinstance(key, tuple):
            key = (0, key)
        try:
            self.__omap.remove(key)
        except ValueError:
            raise KeyError(key)
        return dict.__delitem__(self, key)
    
    def __iter__(self):
        return iter(self.keys())
    
    def __eq__(self, other):
        """
        This only returns true if the k,v pairs of `other`
        are returned in the same order.
        """
        if isinstance(other, dict):
            other = tuple(other.items())
        return other == tuple(self.items())
    
    def __ne__(self, other):
        return not self.__eq__(other) 
    
    def clear(self):
        dict.clear(self)
        self.__omap = list()
    
    def get(self, key, default=None):
        if not isinstance(key, tuple):
            key = (0, key)
        return dict.get(self, key, default)
    
    def iter_items(self):
        return ((key[1], self[key]) for key in self.__omap)        
    
    def items(self):
        return _iter_helper(self.iter_items())
    
    def iter_keys(self):
        return (key[1] for key in self.__omap)
    
    def keys(self):
        return _iter_helper(self.iter_keys())
        
    def iter_values(self): 
        return (self[key] for key in self.__omap)
    
    def values(self):
        return _iter_helper(self.iter_values())

    def update(self, data=None, **kwargs):
        if not data is None:
            if hasattr(data, 'items'):
                data = data.items()
            if not isinstance(data, Iterable):
                raise TypeError('Argument need to provide a items method or be iterable.')
            for kv in data:
                if len(kv) != 2:
                    raise TypeError('Argument, or its keys method need to provide tuples of the length 2.')
                self[kv[0]] = kv[1]
        if len(kwargs) > 0:
            self.update(kwargs)
          
    def get_all_by_key(self, key):
        """ Returns all values of the given key as a generator """
        if not isinstance(key, string_type):
            raise TypeError("Key need to be a string.")
        return (self[d] for d in self.__omap if d[1] == key)
            
    def remove_all_by_key(self, key):
        """ Removes all items with the given key """
        if not isinstance(key, string_type):
            raise TypeError("Key need to be a string.")
        to_del = list()
        for d in self.__omap:
            if d[1] == key:
                to_del.append(d)
        for d in to_del:
            del self[d]
            
        
        