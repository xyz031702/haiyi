import jieba
import unittest

class TestJieba(unittest.TestCase):
    def test_cut_for_search(self):
        product_name = jieba.cut_for_search("sk2")
        print(product_name)
