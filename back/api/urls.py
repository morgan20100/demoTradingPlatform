from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import *
from . import views


router = routers.DefaultRouter()


# router.register('users', UserViewSet)
router.register('product', ProductViewSet)
router.register('subProduct', SubProductViewSet)
router.register('streamPrice', StreamPriceViewSet)
router.register('trade', TradeViewSet)
router.register('pnl', PnlViewSet)
router.register('position', PositionViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
