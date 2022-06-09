from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('create', views.create, name='create'),
    path('student/<int:pk>', views.get_student, name='student'),
    path('edit/<int:pk>', views.edit_student, name='studentEdit'),
    path('login', views.MainLoginView.as_view(), name='login'),
    path('logout', views.MainLogout.as_view(), name='logout'),
    path('load', views.load_file, name='load'),
]
