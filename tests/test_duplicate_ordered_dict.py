import unittest
from vdf import DuplicateOrderedDict


class DuplicateOrderedDict_test(unittest.TestCase):
    map_test = (
            (1, 2),
            (4, 3),(4, 3),(4, 2),
            (7, 2),
            (1, 2),
        )

    def test_keys(self):
        _dict = DuplicateOrderedDict(self.map_test)
        self.assertSequenceEqual(
            tuple(_dict.keys()),
            tuple(x[0] for x in self.map_test))
        
    def test_values(self):
        _dict = DuplicateOrderedDict(self.map_test)
        self.assertSequenceEqual(
            tuple(_dict.values()),
            tuple(x[1] for x in self.map_test))
        
    def test_items(self):
        _dict = DuplicateOrderedDict(self.map_test)
        self.assertSequenceEqual(
            tuple(_dict.items()),
            self.map_test)
        
    def test_direct_access_set(self):
        a = {1:2, 3:4, 5:6}
        b = DuplicateOrderedDict()
        for k,v in a.items():
            b[k] = v
        self.assertDictEqual(a, b)
        
    def test_direct_access_get(self):
        b = dict()
        a = DuplicateOrderedDict({1:2, 3:4, 5:6})
        for k,v in a.items():
            b[k] = v
        self.assertDictEqual(a, b)
        
    def test_update(self):
        a = DuplicateOrderedDict(((1,2),(1,2),(5,3),(1,2)))
        b = DuplicateOrderedDict()
        b.update(((1,2),(1,2)))
        b.update(((5,3),(1,2)))
        self.assertSequenceEqual(tuple(a.items()), tuple(b.items()))
        
    def test_update_2(self):
        self.assertSequenceEqual(
            tuple(DuplicateOrderedDict(self.map_test).items()),
            tuple(DuplicateOrderedDict(DuplicateOrderedDict(self.map_test)).items()))
        
        
        
        