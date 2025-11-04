# Zibal interview task

You need to implement a small service that exposes an API for transaction reports (daily/weekly/monthly) supporting two aggregation types (count and amount). Because the transactions dataset can be very large, the app supports precomputed summaries stored in a transaction_summary collection for fast reads and a fallback on-the-fly aggregation for ad-hoc computation. An optional second part of the project is a notification service (async, retries, multi-channel) — implementing it is optional but recommended.

## 🔧 Run
```bash
git clone https://github.com/mo1ein/zibal.git
cd zibal
```
Then:
```bash
make env
make build
make up
```
Now you can enjoy the app. <br />

## 🌐 Endpoints

```bash
curl http://localhost:8000/api/reports/transactions/?type=count&mode=daily
```

```bash
curl http://localhost:8000/api/reports/transactions/?type=count&mode=weekly
```

```bash
curl http://localhost:8000/api/reports/transactions/?type=count&mode=monthly
```

```bash
curl http://localhost:8000/api/reports/transactions/?type=amount&mode=monthly
```

```bash
curl http://localhost:8000/api/reports/transactions/?type=amount&mode=daily
```

```bash
curl http://localhost:8000/api/reports/transactions/?type=amount&mode=weekly
```


### Successful Response
```json
[
  {
    "key": "هفته ۶ سال ۱۴۰۳",
    "value": 98
  },
  {
    "key": "هفته ۷ سال ۱۴۰۳", 
    "value": 145
  }
]
```

```json
[
  {
    "key": "1402 خرداد",
    "value": 1029
  },
  {
    "key": "1402 تیر",
    "value": 1519
  },
  {
    "key": "1402 مرداد",
    "value": 1519
  }
]
```
