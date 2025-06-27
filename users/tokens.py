from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from decouple import config


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']

        response_data = {
            'access': access,
        }

        response = Response(response_data, status=status.HTTP_200_OK)

        DEBUG = config("DEBUG", default=False, cast=bool)

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=not DEBUG,
            samesite='Lax',
            max_age=7*24*60*60,   # 7 days
        )

        return response


class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail': 'Refresh token cookie not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = {'refresh': refresh_token}

        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
