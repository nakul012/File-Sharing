from upload_download.models import FileUpload, User
from upload_download.serializers import (
    LoginSerializer,
    FileUploadSerializer,
    UserSerializer,
)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import mixins, generics
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import boto3


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=200)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        request.user.auth_token.delete()
        django_logout(request)
        return Response({"Message": "successfully logout"}, status=204)


class ClientRegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.filter(email=request.data['email']).last()
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify')
            absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            email_body = 'Hi '+user.username + \
                ' Use the link below to verify your email \n' + absurl
            data1 = {'email_body': email_body, 'to_email': user.email,
                     'email_subject': 'Verify your email'}

            Util.send_email(data1)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class VerifyEmail(generics.GenericAPIView):
    def get(self):
        pass


class UploadView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        user_id = request.data["user"]

        if User.objects.get(id=user_id).is_ops is True:
            file_serializer = FileUploadSerializer(data=request.data)
            if file_serializer.is_valid():
                file_serializer.save()
                title = request.data["title"]
                s3 = boto3.client('s3')
                s3.upload_file(title, 'upload132', title)
                return Response(file_serializer.data, status=201)
            else:
                return Response(file_serializer.errors, status=400)
        else:
            return Response({"message": "please provide operational user"})


class DownloadUrlView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        url = {
            'download-link': "http://127.0.0.1:8000/download/"f'{pk}', "message": "success"
        }
        return Response(url)


class DownloadView(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        import ipdb
        ipdb.set_trace()
        if request.user.is_ops is False:
            obj = FileUpload.objects.get(pk=pk)
            title = obj.title
            path = "E:/New folder (2)/"
            s3 = boto3.client('s3')
            s3.download_file("upload132", title, path + title)
            return Response({'message': "successfull"})
        else:
            return Response({"message": "only client user allowed"}, status=401)


# class DownloadView(generics.ListAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, pk, format=None):
#         # import ipdb; ipdb.set_trace()
#         a= File.objects.get(pk=pk)
#         file=a.file
#         s3=boto3.client('s3')
#         response=s3.generate_presigned_url(
#         'get_object',
#         Params = {'Bucket': 'upload132', 'Key': str(file)},
#         ExpiresIn = 3600,
#         # request.user.is_client=True
#         )
#         return Response(response)


class UserListView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):

        params = request.query_params
        print(params)
        if not "pk" in kwargs:
            return self.list(request)
        post = get_object_or_404(User, pk=kwargs["pk"])
        return Response(UserSerializer(post).data, status=200)


class FileUploadListView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = FileUploadSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = FileUpload.objects.all()

    def get(self, request, *args, **kwargs):
        if request.user.is_ops is False:
            params = request.query_params
            if not "pk" in kwargs:
                return self.list(request)
            post = get_object_or_404(FileUpload, pk=kwargs["pk"])
            return Response(FileUploadSerializer(post).data, status=200)
        else:
            return Response({"message": "only client access"}, status=401)
