from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from it_cube import settings
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
    path('journal', views.journal, name='journal'),
    path('load-journal', views.load_json)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)