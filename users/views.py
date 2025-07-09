from django.contrib.auth import authenticate
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User, UserSettings
from .utils import get_tokens_for_user
from pdf.models import PDFDocument


from .serializers import UserSerializer, RegisterSerializer, UserSettingsSerializer


class UserDetailView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


user_detail_view = UserDetailView.as_view()


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "User already registered with this email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        stay_logged_in = request.data.get("stay_logged_in", False)
        stay_logged_in = str(stay_logged_in).lower() == "true"
        tokens = get_tokens_for_user(user, stay_logged_in)

        response = Response(
            {
                "message": "User registered successfully.",
                "access": tokens['access'],
            },
            status=status.HTTP_201_CREATED
        )

        response.set_cookie(
            key='refresh_token',
            value=tokens['refresh'],
            httponly=True,
            secure=True,
            samesite='None',
            max_age=7 * 24 * 60 * 60 if stay_logged_in else 60 * 60,
            # domain='pdfai-frontend-sqks.vercel.app',
        )

        return response


register_user_view = RegisterAPIView.as_view()


class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            else:
                return Response(
                    {"message": "Logout successful."},
                    status=status.HTTP_200_OK
                )

            response = Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK
            )

            response.delete_cookie(
                key='refresh_token',
            )
            return response
        except KeyError:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(
                {"error": f"Logout failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


logout_user_view = LogoutAPIView.as_view()


class UserSettingsView(APIView):

    def get(self, request):
        settings, created = UserSettings.objects.get_or_create(
            user=request.user)
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        serializer = UserSettingsSerializer(
            settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


user_settings_view = UserSettingsView.as_view()

User = get_user_model()


class UpdateEmailView(APIView):
    def put(self, request):
        new_email = request.data.get("email")
        if not new_email:
            return Response({"error": "Email is required."}, status=400)

        if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
            return Response({"error": "This email is already taken."}, status=400)

        request.user.email = new_email
        request.user.save()

        return Response({"message": "Email updated successfully."})


update_email_view = UpdateEmailView.as_view()


class UpdatePasswordView(APIView):
    def put(self, request):
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not password or not confirm_password:
            return Response({"error": "Both password fields are required."}, status=400)

        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        try:
            validate_password(password, user=request.user)
        except ValidationError as e:
            return Response({"error": e.messages[0]}, status=400)

        request.user.set_password(password)
        request.user.save()

        return Response({"message": "Password updated successfully. Please log in again."})


update_password_view = UpdatePasswordView.as_view()


class DeleteAccountView(APIView):
    def delete(self, request):
        password = request.data.get("password")
        user = request.user

        if not password:
            return Response(
                {"error": "Password is required to delete account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Incorrect password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # delete pdf documents associated with the user which deletes all chat session
        # which in turn deletes all messages.
        PDFDocument.objects.filter(user=request.user).delete()

        user_email = user.email
        user.delete()

        return Response(
            {"message": f"User {user_email} deleted."},
            status=status.HTTP_200_OK,
        )


delete_account_view = DeleteAccountView.as_view()
