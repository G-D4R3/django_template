from django.urls import path, include
from rest_framework.routers import SimpleRouter

app_name = 'accounts'

router = SimpleRouter()

urlpatterns = [
    path('', include((router.urls, 'accounts'))),
]
