from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Account, Transaction
from .serializers import (
    UserSerializer,
    AccountSerializer,
    TransactionSerializer,
)

from decimal import Decimal

# User Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Automatically create a bank account for the new user
        Account.objects.create(user=user)

# Account Views
class AccountView(generics.RetrieveAPIView):
    queryset = Account.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AccountSerializer

    def get_object(self):
        return self.request.user.accounts.first() # Assumes a user has at least one account

# Transaction Views
class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        account = request.user.accounts.first()
        if not account:
            return Response({"detail": "User has no bank account."}, status=status.HTTP_400_BAD_REQUEST)
        
        amount_str = request.data.get('amount')
        try:
            amount = Decimal(amount_str) # Convert to Decimal
        except (ValueError, TypeError):
            return Response({"detail": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"detail": "Invalid deposit amount."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            account.balance += amount
            account.save()
            
            Transaction.objects.create(
                account=account,
                transaction_type='deposit',
                amount=amount,
                description=request.data.get('description', 'Deposit')
            )
            
        return Response({"detail": f"Successfully deposited {amount} to your account."}, status=status.HTTP_200_OK)

class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        account = request.user.accounts.first()
        if not account:
            return Response({"detail": "User has no bank account."}, status=status.HTTP_400_BAD_REQUEST)
        
        amount_str = request.data.get('amount')
        try:
            amount = Decimal(amount_str) # Convert to Decimal
        except (ValueError, TypeError):
            return Response({"detail": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"detail": "Invalid withdrawal amount."}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            if account.balance < amount:
                return Response({"detail": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)
            
            account.balance -= amount
            account.save()
            
            Transaction.objects.create(
                account=account,
                transaction_type='withdrawal',
                amount=amount,
                description=request.data.get('description', 'Withdrawal')
            )
            
        return Response({"detail": f"Successfully withdrew {amount} from your account."}, status=status.HTTP_200_OK)

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__user=user).order_by('-timestamp')
    
    from decimal import Decimal
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Account, Transaction

# ... existing views ...

class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sender_account = request.user.accounts.first()
        receiver_account_number = request.data.get('receiver_account_number')
        amount_str = request.data.get('amount')
        
        if not sender_account:
            return Response({"detail": "Sender has no bank account."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = Decimal(amount_str)
            receiver_account = Account.objects.get(account_number=receiver_account_number)
        except Account.DoesNotExist:
            return Response({"detail": "Receiver account not found."}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"detail": "Invalid transfer amount."}, status=status.HTTP_400_BAD_REQUEST)

        if sender_account == receiver_account:
            return Response({"detail": "Cannot transfer to the same account."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if sender_account.balance < amount:
                return Response({"detail": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

            # Deduct from sender
            sender_account.balance -= amount
            sender_account.save()
            Transaction.objects.create(
                account=sender_account,
                transaction_type='transfer',
                amount=amount,
                description=f"Transfer to {receiver_account.user.username}"
            )

            # Add to receiver
            receiver_account.balance += amount
            receiver_account.save()
            Transaction.objects.create(
                account=receiver_account,
                transaction_type='transfer',
                amount=amount,
                description=f"Transfer from {sender_account.user.username}"
            )
            
        return Response({"detail": f"Successfully transferred {amount} to account {receiver_account_number}"}, status=status.HTTP_200_OK)
    
    
    from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# ... (other imports) ...
from .models import Transaction
from .serializers import TransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    # Add these two lines for filtering
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transaction_type']

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__user=user).order_by('-timestamp')