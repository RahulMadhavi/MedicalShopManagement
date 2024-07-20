from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, UserSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SignUpView(CreateAPIView):

    permission_classes = [AllowAny]  # Allow access without authentication
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)

        self.send_verification_email(user)

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"http://localhost:4200/accounts/verify-email/{uid}/{token}"
        email_subject = "Verify your email"
        email_body = f"Click the following link to verify your email: {verification_link}"
        print(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse({"detail": "GET method is not allowed"}, status=405)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.profile.email_verified = True
            user.save()
            user.profile.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        csrf_token = get_token(request)
        return Response({"csrf_token": csrf_token})

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except (ArithmeticError, Token.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)
