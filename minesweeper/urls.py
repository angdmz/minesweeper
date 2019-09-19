"""minesweeper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework.authtoken import views as authviews
schema_view = get_swagger_view(title='Minesweeper')

from rest import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'api/v1/games/<int:game_id>', views.GameInteractionView.as_view()),
    url(r'^api/v1/games', views.GamesView.as_view()),
    url(r'api/v1/docs$', schema_view),
    url(r'^api-token-auth/', authviews.obtain_auth_token),
]
