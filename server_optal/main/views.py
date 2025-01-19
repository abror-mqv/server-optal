from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ExchangeRate
from .serializers import ExchangeRateSerializer
from rest_framework.permissions import AllowAny


class ExchangeRateListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        exchange_rates = ExchangeRate.objects.all()
        serializer = ExchangeRateSerializer(exchange_rates, many=True)
        rates = {item['currency_code']: item['rate_to_kgs']
                 for item in serializer.data}
        return Response(rates)
