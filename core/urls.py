from django.urls import path
from django.shortcuts import render, redirect
from . import views

urlpatterns = [
    # ============ Pages (HTML) ============
    path('', views.landing_page, name='landing'),
    
    path('login.html', views.login_page, name='login'),
    path('login', views.login_page, name='login_alias'),
    
    path('register.html', views.register_page, name='register'),
    path('register', views.register_page, name='register_alias'),
    
    path('dashboard.html', views.dashboard_page, name='dashboard'),
    path('dashboard', views.dashboard_page, name='dashboard_alias'),
    
    # ⭐ Data Entry Page (BARU)
    path('data-entry/', views.data_entry_page, name='data_entry'),
    path('data-entry', views.data_entry_page, name='data_entry_alias'),
    path('data-entry.html', views.data_entry_page, name='data_entry_html'),
    
    path(
        'training.html',
        lambda request: render(request, 'training.html')
        if request.user.is_authenticated else redirect('/login.html'),
        name='training'
    ),

    # ============ Auth API ============
    path('api/auth/register', views.api_register, name='api_register'),
    path('api/auth/login', views.api_login, name='api_login'),
    path('api/auth/logout', views.api_logout, name='api_logout'),
    path('api/auth/me', views.api_me, name='api_me'),

    # ============ Flutter API ============
    path('api/data-entry/', views.ambil_data_entry, name='api_data_entry'),

    # ============ Features API ============
    path('api/data-collection', views.api_data_collection, name='api_data_collection'),
    path('api/data-collection/<int:pk>', views.api_data_collection, name='api_data_collection_detail'),

    path('api/analysis', views.api_analysis, name='api_analysis'),
    path('api/analysis/<int:pk>', views.api_analysis, name='api_analysis_detail'),

    path('api/models', views.api_models, name='api_models'),
    path('api/models/<int:pk>', views.api_models, name='api_models_detail'),

    path('api/visualization', views.api_visualization, name='api_visualization'),
    path('api/visualization/<int:pk>', views.api_visualization, name='api_visualization_detail'),

    path('api/training', views.api_training, name='api_training'),
    path('api/training/<int:pk>', views.api_training, name='api_training_detail'),

    path('api/automation', views.api_automation, name='api_automation'),
    path('api/automation/<int:pk>', views.api_automation, name='api_automation_detail'),

    path('api/collaboration', views.api_collaboration, name='api_collaboration'),
    path('api/collaboration/<int:pk>', views.api_collaboration, name='api_collaboration_detail'),

    path('api/insights', views.api_insights, name='api_insights'),
    path('api/insights/<int:pk>', views.api_insights, name='api_insights_detail'),

    path('api/datasets', views.api_dataset, name='api_dataset'),
    path('api/datasets/<int:pk>', views.api_dataset, name='api_dataset_detail'),

    # ============ ML Training & Prediction ============
    path('api/training/start', views.start_training, name='start_training'),
    path('api/predict', views.predict, name='predict'),
    path('api/stats', views.api_stats, name='api_stats'),
    path('api/ml/framing', views.api_ml_framing, name='api_ml_framing'),

    # ============ Submission API ============
    path('api/submissions/receive/', views.api_submission_receive, name='api_submission_receive'),
    path('api/submissions/<int:submission_id>/status/', views.api_submission_status, name='api_submission_status'),
    
    # ⭐ Submissions List (BARU)
    path('api/submissions/list/', views.api_submissions_list, name='api_submissions_list'),
]
