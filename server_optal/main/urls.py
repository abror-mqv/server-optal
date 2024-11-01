from django.urls import path
from .views import CatApiView, RegisterView

urlpatterns = [
    path('cats', CatApiView.as_view(), name='category_tree'),
    path('register/', RegisterView.as_view(), name='register')
    # path('register/', RegisterFactoryUser.as_view(), name='register_factory'),
    # path('subcatlist', SubcatsApiView.as_view()),
]
