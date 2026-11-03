from django.urls import path
from .views import (
    AdminRegisterView,
    AdminLoginView,
    FieldAgentRegisterView,
    FieldAgentLoginView,
    LogoutView,
    ProfileView,
    FieldAgentListView,
    FieldAgentDetailView,
    ToggleAgentActiveView,
)

urlpatterns = [
    # Admin auth
    path('admin/register/', AdminRegisterView.as_view(), name='admin-register'),
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),

    # Field agent auth
    path('agent/register/', FieldAgentRegisterView.as_view(), name='agent-register'),
    path('agent/login/', FieldAgentLoginView.as_view(), name='agent-login'),

    # Shared
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Admin: manage agents
    path('agents/', FieldAgentListView.as_view(), name='agent-list'),
    path('agents/<int:pk>/', FieldAgentDetailView.as_view(), name='agent-detail'),
    path('agents/<int:pk>/toggle-active/', ToggleAgentActiveView.as_view(), name='agent-toggle-active'),
]
