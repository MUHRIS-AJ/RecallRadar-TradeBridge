import unittest
from unittest.mock import patch
import core
class Tests(unittest.TestCase):
    @patch("core.request_json")
    def test_recalls(self,request):
        request.return_value=[{"RecallNumber":"26-001","Title":"Lamp recall","URL":"https://www.cpsc.gov/Recalls/2026/sample"}]
        data=core.recalls("lamp")
        self.assertEqual(data["count"],1)
        self.assertTrue(data["recalls"][0]["product_match_requires_review"])
    @patch("core.request_json")
    def test_trade(self,request):
        request.return_value=[{"page":1},[{"date":"2025","value":12000}]]
        data=core.trade("LK,IN")
        self.assertEqual(len(data["data"]),2)
        self.assertEqual(data["data"][0]["latest_exports_of_goods_and_services"]["value_usd"],12000)
        self.assertEqual(request.call_count,4)
    def test_input_validation(self):
        for bad in ("LK,LK","malicious;curl,IN",""):
            with self.assertRaises(ValueError):core.trade(bad)
        with self.assertRaises(ValueError):core.recalls('foo" OR bar')
if __name__=="__main__":unittest.main()
