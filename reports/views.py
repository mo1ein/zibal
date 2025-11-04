from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReportRequestSerializer
from datetime import datetime
import pymongo
import jdatetime

from .services.mongo_client import get_db

VALID_MODES = {"daily", "weekly", "monthly"}
VALID_TYPES = {"amount", "count"}


def to_jalali_str(dt: datetime, mode: str) -> str:
	"""
	Convert Gregorian datetime to human-readable Jalali string.
	mode: 'daily' -> YYYY/MM/DD
		  'weekly' -> 'هفته N سال YYYY'
		  'monthly'-> 'YYYY MonthName'
	"""
	j = jdatetime.datetime.fromgregorian(datetime=dt)
	if mode == "daily":
		return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"
	elif mode == "weekly":
		# Week number in Jalali year
		start_of_year = jdatetime.date(j.year, 1, 1)
		day_of_year = (j.date() - start_of_year).days + 1
		week_no = (day_of_year - 1) // 7 + 1
		return f"هفته {week_no} سال {j.year}"
	elif mode == "monthly":
		# Persian month names
		month_names = [
			"فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
			"مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
		]
		return f"{j.year} {month_names[j.month - 1]}"
	# fallback to daily
	return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"


class TransactionReportView(APIView):
	"""
	GET /api/reports/transactions/?type=amount|count&mode=daily|weekly|monthly&merchantId=...
	returns: [{ "key": "...", "value": number }, ...]
	"""

	def get(self, request):
		qs = ReportRequestSerializer(data=request.query_params)
		if not qs.is_valid():
			return Response(qs.errors, status=status.HTTP_400_BAD_REQUEST)
		params = qs.validated_data
		agg_type = params["type"]
		mode = params["mode"]
		merchantId = params.get("merchantId")

		db = get_db()
		summary_col = db["transaction_summary"]

		# Try to read precomputed summaries
		query = {"mode": mode, "type": agg_type}
		if merchantId is not None:
			query["merchantId"] = merchantId
		else:
			query["merchantId"] = {"$exists": False}

		docs = list(summary_col.find(query).sort("period_start", pymongo.ASCENDING))

		if docs:
			result = [{"key": d["key"], "value": d["value"]} for d in docs]
			return Response(result)

		# FALLBACK: if no precomputed rows, compute on-the-fly (slower)
		result = self._compute_on_the_fly(db, agg_type, mode, merchantId)
		return Response(result)

	def _compute_on_the_fly(self, db, agg_type, mode, merchantId):
		"""
		Conservative on-the-fly aggregation with Jalali date conversion
		"""
		transactions = db["transaction"]  # Make sure this is your correct collection name

		match = {}
		from bson import ObjectId

		if merchantId:
			try:
				match["merchantId"] = ObjectId(merchantId)
			except:
				# If merchantId is not valid ObjectId, match nothing
				match["merchantId"] = None

		# Group by day first
		pipeline = [
			{"$match": match} if match else {"$match": {}},
			{"$project": {
				"createdAt": {"$toDate": "$createdAt"},
				"amount": 1
			}},
			{"$group": {
				"_id": {
					"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$createdAt"}}
				},
				"sum_amount": {"$sum": {"$ifNull": ["$amount", 0]}},
				"count": {"$sum": 1},
				"first_date": {"$min": "$createdAt"}
			}},
			{"$sort": {"first_date": 1}}
		]

		cursor = transactions.aggregate(pipeline, allowDiskUse=True)
		daily_rows = []
		for r in cursor:
			day_str = r["_id"]["day"]  # 'YYYY-MM-DD'
			dt = datetime.strptime(day_str, "%Y-%m-%d")
			daily_rows.append({
				"date": dt,
				"sum_amount": r["sum_amount"],
				"count": r["count"]
			})

		if not daily_rows:
			return []

		# If mode == daily, convert dates to Jalali
		if mode == "daily":
			out = []
			for r in daily_rows:
				key = to_jalali_str(r["date"], "daily")
				val = r["sum_amount"] if agg_type == "amount" else r["count"]
				out.append({"key": key, "value": val})
			return out

		# For weekly/monthly: aggregate in Gregorian first, then convert to Jalali
		buckets = {}
		for r in daily_rows:
			dt = r["date"]
			if mode == "monthly":
				# Use Gregorian month for aggregation
				key = dt.strftime("%Y-%m")  # e.g. "2024-09"
			elif mode == "weekly":
				# Use Gregorian week for aggregation
				iso = dt.isocalendar()  # (year, week, weekday)
				key = f"{iso[0]}-W{iso[1]:02d}"
			else:
				key = dt.isoformat()

			if key not in buckets:
				buckets[key] = {"sum_amount": 0, "count": 0, "dates": []}
			buckets[key]["sum_amount"] += r["sum_amount"]
			buckets[key]["count"] += r["count"]
			buckets[key]["dates"].append(dt)

		# Convert aggregated buckets to Jalali keys and track the earliest date for sorting
		jalali_data = []
		for gregorian_key, data in buckets.items():
			# Use the first date in the bucket to determine Jalali period
			first_date = min(data["dates"])
			jalali_key = to_jalali_str(first_date, mode)

			val = data["sum_amount"] if agg_type == "amount" else data["count"]
			jalali_data.append({
				"key": jalali_key,
				"value": val,
				"sort_date": first_date  # Use for chronological sorting
			})

		# Sort by the original date to maintain chronological order
		jalali_data.sort(key=lambda x: x["sort_date"])

		# Return only the key-value pairs
		out = [{"key": item["key"], "value": item["value"]} for item in jalali_data]

		return out