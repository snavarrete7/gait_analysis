# tests.py
from src.model import series
import unittest

class TestSeries(unittest.TestCase):
    def test_add_data_serie(self):
        foo = series.Series()

        self.assertEqual(foo.noOfSeries, 0)

        serie1 = [1,4,2,40,0]
        serie2 = [1,0,3,30,4]
        serie3 = [1,2,1,50,0]

        exp_avg = [1, 2, 2, 40, 1.33]
        exp_names = ["serie1", "serie2", "serie3"]

        foo.add_data_serie(serie1, "serie1")
        self.assertEqual(foo.noOfSeries, 1)
        self.assertEqual(foo.get_data_uBound(1), 5)

        foo.add_data_serie(serie2, "serie2")
        foo.add_data_serie(serie3, "serie3")

        #self.assertListEqual(exp_avg, foo.get_avg_serie())
        self.assertListEqual(exp_names, foo.get_series_names())
        self.assertListEqual(serie2, foo.get_data_serie(2-1))
        for i in range(len(exp_avg)):
            self.assertAlmostEqual(exp_avg[i], foo.get_avg_serie()[i], places=2)
        

if __name__ == '__main__':
    unittest.main()