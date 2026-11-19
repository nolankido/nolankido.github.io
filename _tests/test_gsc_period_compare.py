"""Fictional, zero-network regression tests for the private GSC period comparator."""
import copy
from datetime import date
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).with_name("gsc-period-compare.py")
spec = importlib.util.spec_from_file_location("gsc_period_compare", MODULE)
comparator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparator)


def summary(month="2026-08", clicks=25, impressions=1000):
    days, last = comparator.month_days(month)
    return {
        "declared_month": month,
        "declared_window": {"start": month+"-01", "end": last.isoformat()},
        "search_type_declared": "web", "export_date_range_verified": False,
        "chart_export": {"provided": True, "date_format": "iso", "calendar_days_validated": True,
                         "days": days, "clicks": clicks, "impressions": impressions},
        "page_export": {"rows": 3, "outside_site_rows": 1,
                        "observed_section_totals": {x: {"clicks": 0, "impressions": 0, "visible_rows": 0}
                                                    for x in comparator.SECTIONS}},
        "query_export": {"provided": True, "visible_rows": 2, "person_brand_visible_clicks": 3,
                         "tagline_visible_clicks": 1},
        "query_page_export": {"provided": False, "visible_rows": None,
                              "outside_site_rows": None, "visible_nonbrand_technology_clicks": None},
        "property_web_clicks": clicks, "property_web_impressions": impressions,
    }


def month_obj(month, clicks, impressions):
    item = summary(month, clicks, impressions)
    item["page_export"]["observed_section_totals"]["technology"].update(clicks=10, impressions=40, visible_rows=1)
    item["page_export"]["observed_section_totals"]["poker"].update(clicks=5, impressions=30, visible_rows=1)
    return item


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.property = "sc-domain:nolankido.com"

    def parse(self, data):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "private.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return comparator.read_summary(path)

    def compare(self, a, b, as_of=date(2026, 11, 19)):
        return comparator.compare(self.parse(a), self.parse(b), self.property, True, as_of=as_of)

    def test_valid_property_totals_and_partial_visible_data(self):
        out = self.compare(month_obj("2026-08", 25, 1000), month_obj("2026-09", 40, 1500))
        self.assertEqual(out["metrics"]["property_web_clicks"]["change"], 15)
        self.assertEqual(out["metrics"]["property_web_clicks"]["change_pct"], 60)
        self.assertEqual(out["metrics"]["property_web_clicks"]["baseline_per_day"], round(25 / 31, 4))
        self.assertIsNone(out["metrics"]["visible_nonbrand_technology_query_page_clicks"]["change"])
        self.assertFalse(out["property_and_filters_verified_by_tool"])

    def test_zero_baseline_is_not_percent_change(self):
        result = self.compare(month_obj("2026-08", 0, 0), month_obj("2026-09", 5, 10))
        item = result["metrics"]["property_web_clicks"]
        self.assertEqual(item["change"], 5)
        self.assertIsNone(item["change_pct"])
        self.assertEqual(item["status"], "no_percent_baseline")

    def test_missing_chart_means_missing_totals(self):
        before = month_obj("2026-08", 25, 1000)
        before["chart_export"] = {"provided": False, "calendar_days_validated": False, "days": None,
                                  "clicks": None, "impressions": None, "date_format": None}
        before["property_web_clicks"] = None
        before["property_web_impressions"] = None
        result = self.compare(before, month_obj("2026-09", 50, 1200))
        self.assertIsNone(result["metrics"]["property_web_clicks"]["change"])
        self.assertEqual(result["metrics"]["property_web_clicks"]["status"], "unavailable")

    def test_empty_pages_remain_unknown(self):
        before = month_obj("2026-08", 25, 1000)
        before["page_export"] = {"rows": 0, "outside_site_rows": 0,
                                 "observed_section_totals": {x: {"clicks": None, "impressions": None, "visible_rows": 0}
                                                             for x in comparator.SECTIONS}}
        result = self.compare(before, month_obj("2026-09", 30, 900))
        self.assertIsNone(result["metrics"]["technology_exported_page_clicks"]["change"])

    def test_rejects_unconfirmed_filters_and_unrecognized_property(self):
        a, b = self.parse(month_obj("2026-08", 25, 1000)), self.parse(month_obj("2026-09", 40, 1500))
        with self.assertRaises(comparator.ComparisonError):
            comparator.compare(a, b, self.property, False, date(2026, 11, 19))
        with self.assertRaises(comparator.ComparisonError):
            comparator.compare(a, b, "sc-domain:nolankido.com.attacker.net", True, date(2026, 11, 19))

    def test_rejects_future_month_and_out_of_order_months(self):
        with self.assertRaises(comparator.ComparisonError):
            self.compare(month_obj("2026-08", 25, 1000), month_obj("2026-12", 30, 1100))
        with self.assertRaises(comparator.ComparisonError):
            self.compare(month_obj("2026-09", 25, 1000), month_obj("2026-08", 30, 1100))

    def test_rejects_tampered_window_and_inconsistent_chart(self):
        first = month_obj("2026-08", 25, 1000)
        first["declared_window"]["end"] = "2026-08-30"
        with self.assertRaises(comparator.ComparisonError):
            self.parse(first)
        first = month_obj("2026-08", 25, 1000)
        first["chart_export"]["clicks"] = 500
        with self.assertRaises(comparator.ComparisonError):
            self.parse(first)

    def test_rejects_bad_page_rows_and_noninteger_metrics(self):
        first = month_obj("2026-08", 25, 1000)
        first["page_export"]["outside_site_rows"] = 99
        with self.assertRaises(comparator.ComparisonError):
            self.parse(first)
        first = month_obj("2026-08", 25, 1000)
        first["property_web_clicks"] = True
        with self.assertRaises(comparator.ComparisonError):
            self.parse(first)

    def test_rejects_duplicate_or_invalid_query_status(self):
        first = month_obj("2026-08", 25, 1000)
        first["query_export"]["visible_rows"] = 0
        with self.assertRaises(comparator.ComparisonError):
            self.parse(first)


if __name__ == "__main__":
    unittest.main()
