from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.db.models import Sum
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate, get_user_model
from .helper import helper_function , helper_function2

from .models import Buyer_credit, Item_purchased, Item
from .serializers import (
    UsercreditSerializer, 
    ItemPurchasedSerializer, 
    UserSerializer, 
    LoginSerializer, 
    RegisterSerializer,
    ItemSerializer
)

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@swagger_auto_schema(
    security=[{'Bearer': []}]
)


# it shows the buyer credits to the buyer and all buyer credits to the admin user

class Show_buyers(viewsets.ModelViewSet):

    queryset = Buyer_credit.objects.all()
    serializer_class = UsercreditSerializer
    http_method_names = ['get', 'head']
    permission_classes = [IsAuthenticated]

    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
         return Buyer_credit.objects.none()
        user = self.request.user
        if user.is_staff:
            return Buyer_credit.objects.all()
        return Buyer_credit.objects.filter(buyer = user)
    

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return helper_function2(serializer.data, request )

        
    
class Create_buyers_credit(viewsets.ModelViewSet):
    queryset = Buyer_credit.objects.all()
    serializer_class = UsercreditSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['post']

    
    def create(self, request, *args, **kwargs):
        
        credit_amount = request.data.get('credit_amount')
        user = request.data.get('buyer')

        try:
            credit = Buyer_credit.objects.get(buyer= user)
            credit.credit_amount += int(credit_amount)
            credit.save()
            serializer = self.get_serializer(credit)
            return helper_function(serializer.data, "success", status.HTTP_201_CREATED)

            
        except Buyer_credit.DoesNotExist:
            return super().create(request, *args, **kwargs)
        


class show_item_purchased(viewsets.ModelViewSet):
    queryset = Item_purchased.objects.all()
    serializer_class = ItemPurchasedSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'put', 'patch', 'delete', 'head', 'options']


    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()



    def perform_create(self, serializer):
        item_purchased = serializer.save()
        price = item_purchased.item.price
        quantity = item_purchased.quantity
        total_price = price * quantity
        buyer_credit = Buyer_credit.objects.get(buyer=item_purchased.buyer)
        buyer_credit.credit_amount -= total_price
        buyer_credit.save()

    @swagger_auto_schema(security=[{'Bearer': []}])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        return helper_function2(serializer, request)
       


#   user = self.request.user
#         item_purchased = serializer.save(buyer=user)
#         price = item_purchased.item.price
        
#         credit_obj, created = Buyer_credit.objects.get_or_create(buyer=user, defaults={'credit_amount': 300})
#         credit_obj.credit_amount -= price
#         credit_obj.save()

class ItemViewset(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return helper_function2(serializer.data, request)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        return helper_function2(serializer, request)





class Show_UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return helper_function2(serializer.data, request)

class Show_bill(viewsets.ModelViewSet):
    queryset = Item_purchased.objects.all()
    serializer_class = ItemPurchasedSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
          return Item_purchased.objects.none()
        user = self.request.user
        if user.is_staff:
            return Item_purchased.objects.all()
        return Item_purchased.objects.filter(buyer = user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return helper_function2(serializer.data, request)

class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Buyer_credit.objects.create(buyer=user, credit_amount=300)
            tokens = get_tokens_for_user(user)

            # return Response({
            #      "id": user.id,
            #     "username": user.username,
            #     "is_staff": user.is_staff,
            #     "user_type": user.user_type,
            #     "WellCome_message": f"You are logged in {user.username}",
            #     'tokens': tokens,
            #     "tokens": tokens,
            # }, status=status.HTTP_201_CREATED)
            return helper_function(serializer.data, "user registered successfully", status.HTTP_201_CREATED)
        
        return helper_function(serializer.errors, "user registration failed", status=status.HTTP_400_BAD_REQUEST)
            
    
    
    



class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                tokens = get_tokens_for_user(user)
                
                # return Response({
                    
                # "id": user.id,
                # "username": user.username,
                # "is_staff": user.is_staff,
                # "user_type": user.user_type,
                # "WellCome_message": f"You are logged in {user.username}",
                #     'tokens': tokens,
                # }, status=status.HTTP_200_OK)
                return helper_function(tokens , " logged in " , status.HTTP_200_OK)
            return helper_function(None, 'Invalid credentials', status.HTTP_401_UNAUTHORIZED)
        return helper_function(serializer.errors, "Log in failed", status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    

    @swagger_auto_schema(security=[{'Bearer': []}])
    def get(self, request):
        return Response({"message": f"Hello, {request.user.username}!"})



class TokenRefreshView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            return Response({"access": new_access_token}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
