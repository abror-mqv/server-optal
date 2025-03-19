from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..models import Subscription, FactoryProfile
from ..serializers import SubscriptionSerializer, FactoryProfileSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        box_id = request.data.get('box_id')
        # ID для незарегистрированных пользователей
        session_id = request.data.get('session_id')

        if not box_id:
            return Response({'error': 'Box ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        box = get_object_or_404(FactoryProfile, id=box_id)

        if user:
            subscription, created = Subscription.objects.get_or_create(
                user=user, box=box)
        else:
            if not session_id:
                return Response({'error': 'Session ID is required for unauthenticated users.'}, status=status.HTTP_400_BAD_REQUEST)
            subscription, created = Subscription.objects.get_or_create(
                session_id=session_id, box=box)

        if created:
            return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Already subscribed.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_subscriptions(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_403_FORBIDDEN)

        subscriptions = Subscription.objects.filter(user=user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        user = request.user if request.user.is_authenticated else None
        box_id = request.data.get('box_id')
        session_id = request.data.get('session_id')

        if user:
            Subscription.objects.filter(user=user, box_id=box_id).delete()
        elif session_id:
            Subscription.objects.filter(
                session_id=session_id, box_id=box_id).delete()
        else:
            return Response({'error': 'User or session ID required.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Unsubscribed successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_suppliers_info(request):
    supplier_ids = request.data.get('supplier_ids')

    if not supplier_ids or not isinstance(supplier_ids, list):
        return Response({'error': 'Invalid supplier_ids. Must be a list.'}, status=status.HTTP_400_BAD_REQUEST)

    boxes = FactoryProfile.objects.filter(supplier_id__in=supplier_ids)
    serializer = FactoryProfileSerializer(boxes, many=True)

    return Response(serializer.data)
