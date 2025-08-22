# biology_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# --- Import the new ViewSets ---
from .views import (BiologyClassViewSet, StudentViewSet, CommentViewSet, TestViewSet, 
                    QuestionViewSet, StandardViewSet, dashboard_stats)

router = DefaultRouter()
router.register(r'classes', BiologyClassViewSet, basename='biologyclass')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'comments', CommentViewSet, basename='comment')
# --- Register the new ViewSets ---
router.register(r'tests', TestViewSet, basename='test')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'standards', StandardViewSet, basename='standard')

urlpatterns = [
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    path('', include(router.urls)),
]