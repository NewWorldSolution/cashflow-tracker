from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


TWO_PLACES = Decimal("0.01")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def vat_amount(gross: Decimal, vat_rate: float) -> Decimal:
    rate = Decimal(str(vat_rate))
    result = gross - (gross / (Decimal("1") + (rate / Decimal("100"))))
    return _quantize(result)


def net_amount(gross: Decimal, vat_rate: float) -> Decimal:
    return _quantize(gross - vat_amount(gross, vat_rate))


def vat_reclaimable(
    gross: Decimal, vat_rate: float, vat_deductible_pct: float
) -> Decimal:
    result = vat_amount(gross, vat_rate) * Decimal(str(vat_deductible_pct)) / Decimal(
        "100"
    )
    return _quantize(result)


def effective_cost(
    gross: Decimal, vat_rate: float, vat_deductible_pct: float
) -> Decimal:
    vat = vat_amount(gross, vat_rate)
    pct = Decimal(str(vat_deductible_pct))
    result = net_amount(gross, vat_rate) + (
        vat * (Decimal("1") - (pct / Decimal("100")))
    )
    return _quantize(result)
