from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


TWO_PLACES = Decimal("0.01")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _as_decimal(value: Decimal | float | int | str | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def vat_amount(
    gross: Decimal,
    vat_rate: float | int | str | None,
    *,
    vat_mode: str = "automatic",
    manual_vat_amount: Decimal | float | int | str | None = None,
) -> Decimal:
    if vat_mode == "manual":
        return _quantize(_as_decimal(manual_vat_amount) or Decimal("0"))

    rate = _as_decimal(vat_rate) or Decimal("0")
    result = gross - (gross / (Decimal("1") + (rate / Decimal("100"))))
    return _quantize(result)


def net_amount(
    gross: Decimal,
    vat_rate: float | int | str | None,
    *,
    vat_mode: str = "automatic",
    manual_vat_amount: Decimal | float | int | str | None = None,
) -> Decimal:
    return _quantize(
        gross
        - vat_amount(
            gross,
            vat_rate,
            vat_mode=vat_mode,
            manual_vat_amount=manual_vat_amount,
        )
    )


def vat_reclaimable(
    gross: Decimal,
    vat_rate: float | int | str | None,
    vat_deductible_pct: float | int | str | None = None,
    *,
    vat_mode: str = "automatic",
    manual_vat_amount: Decimal | float | int | str | None = None,
    manual_vat_deductible_amount: Decimal | float | int | str | None = None,
) -> Decimal:
    if vat_mode == "manual":
        return _quantize(_as_decimal(manual_vat_deductible_amount) or Decimal("0"))

    pct = _as_decimal(vat_deductible_pct) or Decimal("0")
    result = (
        vat_amount(
            gross,
            vat_rate,
            vat_mode=vat_mode,
            manual_vat_amount=manual_vat_amount,
        )
        * pct
        / Decimal("100")
    )
    return _quantize(result)


def effective_cost(
    gross: Decimal,
    vat_rate: float | int | str | None,
    vat_deductible_pct: float | int | str | None = None,
    *,
    vat_mode: str = "automatic",
    manual_vat_amount: Decimal | float | int | str | None = None,
    manual_vat_deductible_amount: Decimal | float | int | str | None = None,
) -> Decimal:
    vat = vat_amount(
        gross,
        vat_rate,
        vat_mode=vat_mode,
        manual_vat_amount=manual_vat_amount,
    )
    reclaimable = vat_reclaimable(
        gross,
        vat_rate,
        vat_deductible_pct,
        vat_mode=vat_mode,
        manual_vat_amount=manual_vat_amount,
        manual_vat_deductible_amount=manual_vat_deductible_amount,
    )
    result = net_amount(
        gross,
        vat_rate,
        vat_mode=vat_mode,
        manual_vat_amount=manual_vat_amount,
    ) + (vat - reclaimable)
    return _quantize(result)
