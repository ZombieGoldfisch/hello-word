import unittest
from routing import (
    parse_travel_time,
    parse_time_to_minutes,
    minutes_to_hhmm,
    load_graph_from_csv,
    find_route,
    find_nearest_stop,
)

class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph_from_csv("Test_CSV_with_travel_times.csv")

    def test_parse_travel_time(self):
        self.assertAlmostEqual(parse_travel_time("0 days 01:23:45"), 83.75)
        self.assertAlmostEqual(parse_travel_time("1:23:45"), 83.75)
        self.assertEqual(parse_travel_time(""), 0.0)

    def test_parse_time_to_minutes(self):
        self.assertEqual(parse_time_to_minutes("0 days 00:02:00"), 2.0)

    def test_minutes_to_hhmm(self):
        self.assertEqual(minutes_to_hhmm(75), "01:15")
        self.assertEqual(minutes_to_hhmm(24 * 60 + 5), "00:05")

    def test_load_graph(self):
        self.assertIn("Oberderdingen Freibad", self.graph.nodes)
        node = self.graph.nodes["Oberderdingen Freibad"]
        self.assertAlmostEqual(node.lat, 49.05840313, places=5)
        self.assertAlmostEqual(node.lon, 8.79699496, places=5)

    def test_find_route(self):
        start = "Oberderdingen Freibad"
        goal = "Knittlingen ZOB / Schule"
        start_time = 14 * 60 + 29
        path = find_route(self.graph, start, goal, start_minutes=start_time)
        self.assertIsNotNone(path)
        self.assertEqual(path[0][0], start)
        self.assertEqual(path[-1][0], goal)

    def test_find_nearest_stop(self):
        stop = find_nearest_stop(self.graph, (49.0584, 8.7970))
        self.assertEqual(stop, "Oberderdingen Freibad")


class ClassifyQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph_from_csv("Test_CSV_with_travel_times.csv")
        cls.stop_names = list(cls.graph.nodes.keys())

    def setUp(self):
        # Provide dummy modules so ``cli`` can be imported without optional
        # dependencies installed.
        import sys, types
        sys.modules.setdefault("osmnx", types.ModuleType("osmnx"))
        sys.modules.setdefault("networkx", types.ModuleType("networkx"))
        sys.modules.setdefault("folium", types.ModuleType("folium"))
        from importlib import reload
        import cli as cli_module
        reload(cli_module)
        self.classify_query = cli_module.classify_query

    def test_case_insensitive(self):
        stop, coords = self.classify_query("oberderdingen freibad", self.stop_names)
        self.assertEqual(stop, "Oberderdingen Freibad")
        self.assertIsNone(coords)

    def test_minor_typo(self):
        stop, coords = self.classify_query("Oberderdingen Frebad", self.stop_names)
        self.assertEqual(stop, "Oberderdingen Freibad")
        self.assertIsNone(coords)

    def test_lower_cutoff_match(self):
        stop, coords = self.classify_query("Oberderdingen", self.stop_names)
        self.assertEqual(stop, "Oberderdingen Amthof")
        self.assertIsNone(coords)

    def test_geocode_invoked_for_address(self):
        # Queries that look like real addresses should trigger geocoding
        from unittest.mock import patch

        query = "Musterstrasse 5, Teststadt"
        with patch("cli.geocode_address", return_value=(1.0, 2.0)) as geo:
            stop, coords = self.classify_query(query, self.stop_names)
            geo.assert_called_once_with(query)
            self.assertIsNone(stop)
            self.assertEqual(coords, (1.0, 2.0))

    def test_address_skips_stop_matching(self):
        # Ensure address strings do not go through fuzzy stop matching
        from unittest.mock import patch

        query = "Hauptstrasse 12"
        with patch("cli.resolve_stop", side_effect=AssertionError("called")):
            with patch("cli.geocode_address", return_value=(3.0, 4.0)):
                stop, coords = self.classify_query(query, self.stop_names)
                self.assertIsNone(stop)
                self.assertEqual(coords, (3.0, 4.0))


if __name__ == "__main__":
    unittest.main()
