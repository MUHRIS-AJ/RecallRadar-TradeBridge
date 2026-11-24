import unittest
from unittest.mock import patch
import core

class FoodTests(unittest.TestCase):
    @patch("core.request_json")
    def test_fda_food_query(self,fetch):
        fetch.return_value={"results":[{"recall_number":"F-123","product_description":"Example cheese","report_date":"20261101"}]}
        result=core.run("food:cheese","RecallRadar")
        self.assertEqual(result["count"],1)
        self.assertEqual(result["recalls"][0]["official_provider"],"US FDA")
        self.assertIn("fda.gov",fetch.call_args.args[0])
    def test_bad_input(self):
        with self.assertRaises(ValueError):core.food_recalls('bad " query')
if __name__=="__main__":unittest.main()
