from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from it_cube import settings
from main import views, views_student, views_journal, views_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('create', views_student.create, name='create'),
    path('student/<int:pk>', views_student.get_student, name='student'),
    path('edit/<int:pk>', views_student.edit_student, name='studentEdit'),
    path('login', views.MainLoginView.as_view(), name='login'),
    path('logout', views.MainLogout.as_view(), name='logout'),
    path('load', views.load_file, name='load'),
    path('journal', views_journal.journal, name='journal'),
    path('load-journal', views_journal.load_json),
    path('profile', views_user.user_profile, name="profile")
]

handler404 = views.error404_handler
handler403 = views.error403_handler

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)