from datetime import datetime

import jdatetime


def to_jalali_str(dt: datetime, mode: str) -> str:
    """
    Convert Gregorian datetime to human-readable Jalali string.
    mode: 'daily' -> YYYY/MM/DD
          'weekly' -> 'YYYY Week N'   (we will compute week number in Jalali year)
          'monthly'-> 'YYYY MonthName' (we output '1403 Shahrivar' style)
    NOTE: We keep output format similar to PDF examples (year and Persian month names)
    """
    j = jdatetime.datetime.fromgregorian(datetime=dt)
    if mode == "daily":
        return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"
    if mode == "weekly":
        # Week number inside Jalali year: compute day-of-year then week index
        start_of_year = jdatetime.date(j.year, 1, 1)
        day_of_year = (j.date() - start_of_year).days + 1
        week_no = (day_of_year - 1) // 7 + 1
        return f"{j.year} سال {week_no} ھفتھ"
    if mode == "monthly":
        # Persian month names
        month_names = [
            "فروردین",
            "اردیبهشت",
            "خرداد",
            "تیر",
            "مرداد",
            "شھریور",
            "مھر",
            "آبان",
            "آذر",
            "دی",
            "بهمن",
            "اسفند",
        ]
        return f"{j.year} {month_names[j.month - 1]}"
    # fallback to daily
    return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"
