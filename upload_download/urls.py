from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from upload_download.views import DownloadView,DownloadUrlView,FileUploadListView,VerifyEmail, UploadView,ClientRegisterView,UserListView,LoginView

urlpatterns = [
    path('upload', UploadView.as_view() ),
    path('register/client', ClientRegisterView.as_view() ),
    path('user', UserListView.as_view() ),
    path('login', LoginView.as_view() ),
    path('download-file/<int:pk>', DownloadUrlView.as_view() ),
    path('download/<int:pk>', DownloadView.as_view() ),
    path('list_uploaded_files', FileUploadListView.as_view() ),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
]



if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)