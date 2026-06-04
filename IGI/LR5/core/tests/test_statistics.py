from core.statistics import sale_amount_stats


def test_empty_sales_stats():
    class QS:
        def values_list(self, *a, **k):
            return []

    assert sale_amount_stats(QS())['count'] == 0
