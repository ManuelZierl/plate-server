import unittest
from app import app, db
from utils import is_german_plate, levenshtein_distance


class TestApp(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQL_ALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_plate_post_and_get(self):
        cases = [
            ["M-ZG134", True],
            ["MHL-H8866", True],
            ["AÖ-Ih4", True],
            ["QLB-kL77", True],
            ["M-Ä123", False],  # umlaut after the hyphen
            ["1-ZG123", False],  # numbers at start
            ["M-ZG023", False],  # numbers start with 0
            ["MZG123", False],  # hyphen missing
        ]

        for plate_str, valid in cases:
            response = self.client.post("/plate", data={"plate": plate_str})
            self.assertEqual(response.status_code, 200 if valid else 422)
            json_response = response.get_json()
            if valid:
                self.assertEqual(json_response.get("plate"), plate_str)
            self.assertEqual(json_response.get("success"), valid)

        response = self.client.get("/plate")
        json_response = response.get_json()
        self.assertEqual(len(json_response), 4)
        self.assertEqual(set(x["plate"] for x in json_response), {
            "M-ZG134",
            "MHL-H8866",
            "AÖ-Ih4",
            "QLB-kL77"
        })

    def test_plate_search(self):
        plates = ["M-ZG134", "ÖR-ZG134", "M-Z1002", "A-G104", "A-ZG134"]
        for plt in plates:
            self.client.post("/plate", data={"plate": plt})

        response = self.client.get("/search-plate?key=MZG134&levenshtein=0")
        self.assertEqual(set(x["plate"] for x in response.get_json()["MZG134"]), {"M-ZG134"})

        response = self.client.get("/search-plate?key=MZG134&levenshtein=1")
        self.assertEqual(set(x["plate"] for x in response.get_json()["MZG134"]), {"M-ZG134", "A-ZG134"})

        response = self.client.get("/search-plate?key=MZG134&levenshtein=2")
        self.assertEqual(set(x["plate"] for x in response.get_json()["MZG134"]), {"M-ZG134", "ÖR-ZG134", "A-ZG134"})

        response = self.client.get("/search-plate?key=MZG134&levenshtein=3")
        self.assertEqual(set(x["plate"] for x in response.get_json()["MZG134"]),
                         {"M-ZG134", "ÖR-ZG134", "A-G104", "A-ZG134"})

        response = self.client.get("/search-plate?key=MZG134&levenshtein=4")
        self.assertEqual(set(x["plate"] for x in response.get_json()["MZG134"]),
                         {"M-ZG134", "ÖR-ZG134", "M-Z1002", "A-G104", "A-ZG134"})

        response = self.client.get("/search-plate?key=MZG134&levenshtein=notanint")
        self.assertFalse(response.get_json()["success"])
        self.assertEqual(response.status_code, 400)

        response = self.client.get("/search-plate?levenshtein=2")
        self.assertFalse(response.get_json()["success"])
        self.assertEqual(response.status_code, 400)


class TestUtils(unittest.TestCase):
    def test_is_german_plate(self):
        self.assertTrue(is_german_plate("MÜR-AB1234"))
        self.assertTrue(is_german_plate("N-C33"))
        self.assertTrue(is_german_plate("NE-A2"))
        self.assertTrue(is_german_plate("NES-ZU6"))
        self.assertFalse(is_german_plate("MÜRAB1234"))  # no hypne
        self.assertFalse(is_german_plate("N-Ä33"))  # umlaut after hypne
        self.assertFalse(is_german_plate("NE-A02"))  # starting 0
        self.assertFalse(is_german_plate("NES-ZU66667"))  # too long

    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("banana", "banana"), 0)
        self.assertEqual(levenshtein_distance("banana", "ananas"), 2)
        self.assertEqual(levenshtein_distance("banana", "bahamas"), 3)
        self.assertEqual(levenshtein_distance("banana", "apple"), 5)
        self.assertEqual(levenshtein_distance("", "apple"), 5)
        self.assertEqual(levenshtein_distance("banana", ""), 6)


if __name__ == '__main__':
    unittest.main()
