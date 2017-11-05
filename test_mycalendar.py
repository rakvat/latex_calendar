import unittest

import mycalendar


class MyLatexCalendarTest(unittest.TestCase):
    def setUp(self):
        self.subject = mycalendar.LatexCalendarData()

    def test_get_data(self):
        data = { "x": 3 }
        result = self.subject.get_data(data, "x")
        self.assertEqual(result, 3)
        result = self.subject.get_data(data, "y")
        self.assertEqual(result, "")

    def test_init_year_map(self):
        self.subject.init_year_map(2018)
        self.assertEqual(len(self.subject.year_map[1]), 31)

    def test_get_all_categories(self):
        events = { "a": [ { "category": 1 }, { "category": 2 } ], "b": [{ "category": 3 } ] }
        result = self.subject.get_all_categories(events)
        self.assertEqual(result, [1, 2, 3])

    def test_handle_event(self):
        self.subject.chosen_categories = ["category"]
        self.subject.init_year_map(2018)
        event1 = { "label": "label", "category": "category", "month": 3, "n": 1, "weekday": 0 }
        event2 = { "label": "label", "category": "", "month": 3, "n": 1, "weekday": 0 }
        self.subject.handle_event(2018, event2, "nth_weekday_in_month_events")
        self.assertEqual(self.subject.year_map[3][5], [])
        self.subject.handle_event(2018, event1, "nth_weekday_in_month_events")
        self.assertEqual(self.subject.year_map[3][5], ["label"])


class MyCalendarTest(unittest.TestCase):
    def setUp(self):
        self.subject = mycalendar.LatexCalendar()

    def test_format_year(self):
        output = self.subject.format_year(2018)
        self.assertTrue("2018" in output)
        self.assertTrue("December" in output)
        self.assertTrue("\end{document}" in output)
