from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'labeling'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<uuid:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<uuid:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    
    path('datasets/create/<uuid:project_id>/', views.DatasetCreateView.as_view(), name='dataset_create'),
    path('datasets/<uuid:pk>/', views.DatasetDetailView.as_view(), name='dataset_detail'),
    path('datasets/<uuid:pk>/edit/', views.DatasetUpdateView.as_view(), name='dataset_edit'),
    path('datasets/<uuid:pk>/upload/', views.ImageUploadView.as_view(), name='image_upload'),
    
    path('images/<uuid:pk>/', views.ImageDetailView.as_view(), name='image_detail'),
    path('images/<uuid:pk>/annotate/', views.AnnotationView.as_view(), name='annotate_image'),
    
    path('api/annotations/', views.AnnotationAPIView.as_view(), name='annotation_api'),
    path('api/annotations/<uuid:pk>/', views.AnnotationAPIView.as_view(), name='annotation_api_detail'),
    
    path('export/<uuid:dataset_id>/<str:format>/', views.ExportDatasetView.as_view(), name='export_dataset'),
    
    # Authentication
    path('login/', LoginView.as_view(template_name='labeling/login.html', next_page='labeling:project_list'), name='login'),
    path('logout/', LogoutView.as_view(next_page='labeling:project_list'), name='logout'),
]