# app/utils/formatting.py

import locale

def format_cop(value):
    """
    Formats a numeric value into a Colombian Peso (COP) string representation.
    - Removes decimal part.
    - Uses a dot '.' as a thousands separator.
    """
    if value is None:
        value = 0
    
    try:
        # Convert to integer to remove decimals
        int_value = int(float(value))
        # Format with thousand separators
        return f"{int_value:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def unformat_cop(value_str):
    """
    Converts a COP formatted string back to a numeric value.
    - Removes dot separators.
    """
    if not isinstance(value_str, str):
        return value_str
    
    # Remove dots and convert to integer
    try:
        return int(value_str.replace(".", ""))
    except ValueError:
        return 0

