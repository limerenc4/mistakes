# mistake_manager/urls.py
from django.contrib import admin
from django.urls import path
from mistake_app import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('add/', views.add_mistake, name='add'),
    path('list/', views.mistake_list, name='list'),
    path('stats/', views.statistics, name='stats'),
    path('export/', views.export_page, name='export_page'),      # 展示页面
    path('export/download/', views.export_data, name='export'), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   
