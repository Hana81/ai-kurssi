from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostDeleteView, CommentCreateView, CustomLogoutView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('new/', PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('<int:post_pk>/comment/new/', CommentCreateView.as_view(), name='comment-create'),
]
