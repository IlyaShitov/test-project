from decimal import Decimal, ROUND_DOWN


def round_decimal(decimal: Decimal) -> Decimal:
    """
    Help function to round Decimal
    """
    return Decimal(decimal).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

