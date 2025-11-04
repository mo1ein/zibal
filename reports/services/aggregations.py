from datetime import datetime

from pymongo import UpdateOne

from .mongo_client import get_db
from .utils import to_jalali_str


def build_and_store_summary(batch_size=1000):
    """
    Full re-compute: For performance you may prefer incremental updates.
    Steps:
     - Aggregate transactions grouped by day/week/month and merchant (including global null merchant)
     - Upsert results into transaction_summary
    """
    db = get_db()
    tx = db.transactions

    # 1) Daily aggregation (group by year-month-day)
    pipeline_daily = [
        {"$match": {"status": {"$ne": "failed"}}},  # example filter - adjust as needed
        {
            "$project": {
                "amount": 1,
                "merchant_id": 1,
                "created_at": 1,
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            }
        },
        {
            "$group": {
                "_id": {"date": "$date", "merchant_id": "$merchant_id"},
                "count": {"$sum": 1},
                "amount": {"$sum": "$amount"},
            }
        },
    ]

    # 2) Weekly aggregation: use $isoWeekYear + $isoWeek with created_at
    pipeline_weekly = [
        {"$match": {"status": {"$ne": "failed"}}},
        {
            "$project": {
                "amount": 1,
                "merchant_id": 1,
                "isoWeekYear": {"$isoWeekYear": "$created_at"},
                "isoWeek": {"$isoWeek": "$created_at"},
            }
        },
        {
            "$group": {
                "_id": {"year": "$isoWeekYear", "week": "$isoWeek", "merchant_id": "$merchant_id"},
                "count": {"$sum": 1},
                "amount": {"$sum": "$amount"},
            }
        },
    ]

    # 3) Monthly aggregation (year-month)
    pipeline_monthly = [
        {"$match": {"status": {"$ne": "failed"}}},
        {
            "$project": {
                "amount": 1,
                "merchant_id": 1,
                "month": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
            }
        },
        {
            "$group": {
                "_id": {"month": "$month", "merchant_id": "$merchant_id"},
                "count": {"$sum": 1},
                "amount": {"$sum": "$amount"},
            }
        },
    ]

    # Compute and upsert
    for mode, pipeline in (("daily", pipeline_daily), ("weekly", pipeline_weekly), ("monthly", pipeline_monthly)):
        cursor = tx.aggregate(pipeline, allowDiskUse=True)
        ops = []
        for doc in cursor:
            # Build period key ISO and Jalali key
            if mode == "daily":
                iso_key = doc["_id"]["date"]  # 'YYYY-MM-DD'
                # parse to datetime for jalali conversion
                dt = datetime.strptime(iso_key, "%Y-%m-%d")
                jalali_key = to_jalali_str(dt, "daily")
            elif mode == "monthly":
                iso_key = doc["_id"]["month"]  # 'YYYY-MM'
                dt = datetime.strptime(iso_key + "-01", "%Y-%m-%d")
                jalali_key = to_jalali_str(dt, "monthly")
            else:  # weekly
                year = int(doc["_id"]["year"])
                week = int(doc["_id"]["week"])
                # For ISO week -> get Monday of that ISO week in Gregorian:
                # python's fromisocalendar(year, week, 1)
                from datetime import date

                try:
                    d = date.fromisocalendar(year, week, 1)
                except Exception:
                    # fallback
                    d = date(year, 1, 1)
                dt = datetime(d.year, d.month, d.day)
                iso_key = f"{year}-W{week:02d}"
                jalali_key = to_jalali_str(dt, "weekly")

            merchant_id = doc["_id"].get("merchant_id")
            count = int(doc.get("count", 0))
            amount = int(doc.get("amount", 0) or 0)

            upsert_doc = {
                "period_type": mode,
                "period_key_iso": iso_key,
                "period_key_jalali": jalali_key,
                "merchant_id": merchant_id,
                "count": count,
                "amount": amount,
                "updated_at": datetime.utcnow(),
            }

            # upsert by (period_type, period_key_iso, merchant_id)
            filter_q = {"period_type": mode, "period_key_iso": iso_key, "merchant_id": merchant_id}
            ops.append(UpdateOne(filter_q, {"$set": upsert_doc}, upsert=True))

            # flush in batches
            if len(ops) >= batch_size:
                db.transaction_summary.bulk_write(ops)
                ops = []
        if ops:
            db.transaction_summary.bulk_write(ops)

    # Optionally rebuild aggregate for global (merchant_id null) by re-aggregating ignoring merchant grouping
    # That can be done similarly, or the pipelines above will produce entries where merchant_id is null.
    return True
