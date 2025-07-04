from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User
from .utils import get_tokens_for_user


from .serializers import UserSerializer, RegisterSerializer


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

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

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
