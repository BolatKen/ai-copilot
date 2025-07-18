from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.HealthCheckView.as_view(), name="health-check"),
    path("ask/", views.AskView.as_view(), name="copilot-ask"),

    path('upload/', views.upload_content, name='upload_content'),
    path('content/<int:content_id>/status/', views.get_content_status, name='get_content_status'),
    path('content/<int:content_id>/warning/', views.get_submission_warning, name='get_submission_warning'),
    path('content/<int:content_id>/update-status/', views.update_content_status, name='update_content_status'),
    path('moderator/dashboard/', views.moderator_dashboard, name='moderator_dashboard'),
    
    path("unverified/", views.get_unverified_content),
    path("moderation/<int:result_id>/verify/", views.mark_as_verified),
    path("moderation/<int:content_id>/update-tags/", views.update_moderation_tags),
    path('moderation/finalize/<int:content_id>/', views.moderator_finalize_review)


]
