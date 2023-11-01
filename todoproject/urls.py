"""
URL configuration for todoproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from django.conf import settings

admin.site.site_header = 'Enigmatix'
# admin.site.site_title = 'Admin Site Title'
admin.site.index_title = 'Welcome to the Enigmatix Dashboard'
# # admin.site.site_url = 'enigmtix.io'
# admin.site.disable_action('delete_selected')
# admin.site.actions_on_top = True
# admin.site.actions_on_bottom = False

urlpatterns = [
                  path('admin/', admin.site.urls),
                  # path('', include('todoapp.urls')),
                  path('api-token-auth', views.obtain_auth_token),
                  path('api/token/', obtain_jwt_token, name='token_obtain_pair'),
                  path('api/token/refresh/', refresh_jwt_token, name='token_refresh'),
                  path("chat/", include("chatapp.urls")),
                  path('cms/', include('cms.urls')),
                  path('', include('chatingapp.urls'))
              ] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
