import unittest
from vdf import VDFDict


class DuplicateOrderedDict_test(unittest.TestCase):
    map_test = (
            ("1", 2),
            ("4", 3),("4", 3),("4", 2),
            ("7", 2),
            ("1", 2),
        )

    def test_keys(self):
        _dict = VDFDict(self.map_test)
        self.assertSequenceEqual(
            tuple(_dict.keys()),
            tuple(x[0] for x in self.map_test))
        
    def test_values(self):
        _dict = VDFDict(self.map_test)
        self.assertSequenceEqual(
            tuple(_dict.values()),
            tuple(x[1] for x in self.map_test))
        
    def test_items(self):
        _dict = VDFDict(self.map_test)
        self.assertSequenceEqual(
            tuple(_dict.items()),
            self.map_test)
        
    def test_direct_access_set(self):
        a = {"1":2, "3":4, "5":6}
        b = VDFDict()
        for k,v in a.items():
            b[k] = v
        self.assertDictEqual(a, b)
        
    def test_direct_access_get(self):
        b = dict()
        a = VDFDict({"1":2, "3":4, "5":6})
        for k,v in a.items():
            b[k] = v
        self.assertDictEqual(a, b)
        
    def test_update(self):
        a = VDFDict((("1",2),("1",2),("5",3),("1",2)))
        b = VDFDict()
        b.update((("1",2),("1",2)))
        b.update((("5",3),("1",2)))
        self.assertSequenceEqual(tuple(a.items()), tuple(b.items()))
        
    def test_update_2(self):
        self.assertSequenceEqual(
            tuple(VDFDict(self.map_test).items()),
            tuple(VDFDict(VDFDict(self.map_test)).items()))
        
    def test_del(self):
        """ Tests del """
        a = VDFDict((("1",2),("1",2),("5",3),("1",2)))
        b = VDFDict((("1",2),("1",2),("1",2)))
        del a["5"]
        self.assertSequenceEqual(tuple(a.items()), tuple(b.items()))
        
    def test_remove_all(self):
        a = VDFDict((("1",2),("1",2),("5",3),("1",2)))
        b = VDFDict((("5",3),))
        a.remove_all_by_key("1")
        self.assertSequenceEqual(tuple(a.items()), tuple(b.items()))
        
    def test_clear(self):
        a = VDFDict((("1",2),("1",2),("5",3),("1",2)))
        a.clear()
        self.assertEqual(len(a), 0)
        
    def test_get_all(self):
        a = VDFDict((("1",2),("1",2**31),("5",3),("1",2)))
        self.assertSequenceEqual(
            tuple(a.get_all_by_key("1")),
            (2,2**31,2)) 
        
        
    def test_exception_insert(self):
        """ Only strings (and tuples) are supported as keys """
        a = VDFDict()
        self.assertRaises(TypeError, a.__setitem__, 5, "foo")
        
    def test_exception_remove_all(self):
        """ Only strings are supported as keys """
        a = VDFDict()
        self.assertRaises(TypeError, a.remove_all_by_key, 5)
        
    def test_exception_get_all(self):
        """ Only strings are supported as keys """
        a = VDFDict((("1",2),("1",2**31),("5",3),("1",2)))
        self.assertRaises(TypeError, a.get_all_by_key, 5)
        
        
        
        
        
        
        