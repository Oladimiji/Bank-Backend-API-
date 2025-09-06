from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, AccountView

urlpatterns = [
    # Auth URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Account URLs
    path('account/', AccountView.as_view(), name='account-detail'),
]

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, AccountView, DepositView, WithdrawalView

from .views import TransferView
from .views import TransactionListView
urlpatterns = [
    # Auth URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Account URLs
    path('account/', AccountView.as_view(), name='account-detail'),
    
    # Transaction URLs
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdrawal/', WithdrawalView.as_view(), name='withdrawal'),
    
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),

]