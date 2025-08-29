# account/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from .models import Account
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
import jwt, datetime


@swagger_auto_schema(method="post", request_body=RegisterSerializer,
                     responses={201: "Account created"})
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        account = Account(
            name=serializer.validated_data["name"],
            email=serializer.validated_data["email"]
        )
        account.set_password(serializer.validated_data["password"])
        account.save()
        return Response({"message": "Account created", "id": str(account.id)}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="post", request_body=LoginSerializer,
                     responses={200: "Login successful with JWT token"})
@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        try:
            account = Account.objects.get(email=serializer.validated_data["email"])
            if account.check_password(serializer.validated_data["password"]):
                payload = {
                    "account_id": str(account.id),
                    "exp": datetime.datetime.utcnow() + settings.JWT_EXP_DELTA,
                    "iat": datetime.datetime.utcnow()
                }
                token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
                return Response({"message": "Login successful", "token": token})
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Account.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="get", responses={200: ProfileSerializer()})
@api_view(["GET"])
def profile(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return Response({"error": "Authorization header missing"}, status=status.HTTP_401_UNAUTHORIZED)

    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        account_id = payload.get("account_id")
        account = Account.objects.get(id=account_id)
        serializer = ProfileSerializer(account)
        return Response(serializer.data)
    except jwt.ExpiredSignatureError:
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
