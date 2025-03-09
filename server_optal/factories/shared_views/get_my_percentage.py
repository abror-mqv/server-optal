from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from ..models import FactoryProfile, Product
from ..serializers import ProductInStockSerializer


class GetMyPercentage(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            factory = FactoryProfile.objects.get(user=request.user)
            percentage = factory.get_commission()
            return Response({"percentage": percentage}, status=HTTP_200_OK)
        except FactoryProfile.DoesNotExist:
            return Response({"error": "Профиль не найден"}, status=HTTP_400_BAD_REQUEST)
