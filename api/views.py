# register header
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import BadHeaderError, send_mail
from django.http import request
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.views import APIView
from .serializers import UserSerializer, RegisterSerializer
# login header
from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
# change password
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
# send mail
from django.conf import settings
from django.core.mail import EmailMessage

# Register API


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

# Login API


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import smtplib, ssl, sys
class SendMail(APIView):
    def post(self, request, *args, **kwargs):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "spushpanshu@gmail.com"  # Enter your address
        receiver_email = [request.data["email"]]
        password = "shashi123"
        message = "Subject: "+request.data["subject"]+"\n"+"Your one time pin (OTP) code is: "+request.data['otp']+"\nOTP is valid for the next 15 minutes only.\nIf you are having any issues with your account, please wait\nThanks!\npushpanshuranjansingh.com"
        print(request.data["email"], request.data['otp'])
        # sys.stdout.writelines(lines= request.data["email"] + request.data['otp'])
        # sys.stdout.flush()


        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            return HttpResponse(server.noop())

