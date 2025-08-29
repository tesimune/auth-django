from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Account
import json, jwt, datetime


def account(request, uuid):
    account = Account.objects.get(id=uuid)
    return render(request, 'account/show.html', {'account': account})

@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        account = Account(name=name, email=email)
        account.set_password(password)
        account.save()

        return JsonResponse({"message": "Account created", "id": str(account.id)})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        try:
            account = Account.objects.get(email=email)
            if account.check_password(password):
                payload = {
                    "account_id": str(account.id),
                    "exp": datetime.datetime.utcnow() + settings.JWT_EXP_DELTA,
                    "iat": datetime.datetime.utcnow()
                }
                token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

                return JsonResponse({"message": "Login successful", "token": token})
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        except Account.DoesNotExist:
            return JsonResponse({"error": "Account not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def profile(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization header missing"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        account_id = payload.get("account_id")
        account = Account.objects.get(id=account_id)

        return JsonResponse({
            "id": str(account.id),
            "name": account.name,
            "email": account.email,
            "created_at": account.created_at,
            "updated_at": account.updated_at
        })
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)
    except Account.DoesNotExist:
        return JsonResponse({"error": "Account not found"}, status=404)
