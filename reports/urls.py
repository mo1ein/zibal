from django.urls import path

from reports.views import TransactionReportView

urlpatterns = [
    path("transactions/", TransactionReportView.as_view(), name="transaction.bin-report"),
]
