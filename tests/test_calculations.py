from decimal import Decimal

from app.services.calculations import (
    effective_cost,
    net_amount,
    vat_amount,
    vat_reclaimable,
)


def test_automatic_vat_amount_rate_0():
    assert vat_amount(Decimal("100"), 0) == Decimal("0.00")


def test_automatic_vat_amount_rate_5():
    assert vat_amount(Decimal("105"), 5) == Decimal("5.00")


def test_automatic_vat_amount_rate_8():
    assert vat_amount(Decimal("108"), 8) == Decimal("8.00")


def test_automatic_vat_amount_rate_23():
    assert vat_amount(Decimal("123"), 23) == Decimal("23.00")


def test_automatic_net_amount():
    assert net_amount(Decimal("123"), 23) == Decimal("100.00")


def test_automatic_vat_reclaimable_100():
    assert vat_reclaimable(Decimal("123"), 23, 100) == Decimal("23.00")


def test_automatic_vat_reclaimable_50():
    assert vat_reclaimable(Decimal("123"), 23, 50) == Decimal("11.50")


def test_automatic_vat_reclaimable_0():
    assert vat_reclaimable(Decimal("123"), 23, 0) == Decimal("0.00")


def test_automatic_effective_cost_100pct():
    assert effective_cost(Decimal("123"), 23, 100) == Decimal("100.00")


def test_automatic_effective_cost_50pct():
    assert effective_cost(Decimal("123"), 23, 50) == Decimal("111.50")


def test_automatic_effective_cost_0pct():
    assert effective_cost(Decimal("123"), 23, 0) == Decimal("123.00")


def test_manual_vat_amount_uses_stored_value():
    assert (
        vat_amount(
            Decimal("246"),
            None,
            vat_mode="manual",
            manual_vat_amount="46.00",
        )
        == Decimal("46.00")
    )


def test_manual_net_amount_uses_manual_vat():
    assert (
        net_amount(
            Decimal("246"),
            None,
            vat_mode="manual",
            manual_vat_amount="46.00",
        )
        == Decimal("200.00")
    )


def test_manual_vat_reclaimable_uses_stored_deductible_amount():
    assert (
        vat_reclaimable(
            Decimal("246"),
            None,
            None,
            vat_mode="manual",
            manual_vat_deductible_amount="23.00",
        )
        == Decimal("23.00")
    )


def test_manual_effective_cost_uses_manual_amounts():
    assert (
        effective_cost(
            Decimal("246"),
            None,
            None,
            vat_mode="manual",
            manual_vat_amount="46.00",
            manual_vat_deductible_amount="23.00",
        )
        == Decimal("223.00")
    )
