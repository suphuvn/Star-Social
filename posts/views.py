from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.views import generic
from braces.views import SelectRelatedMixin
from . import models
from . import forms
from django.contrib.auth import get_user_model
from django.contrib import messages
# Create your views here.

User = get_user_model()

# Shows the list of posts related to the user or group
class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ('user', 'group')

# Shows the list of posts related to the user
class UserPosts(generic.ListView):
    model = models.Post
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        # Try to get the query set by fetching posts related to user
        try:
            self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    # Grab post user and return context dictionary
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context

# Select post's detail
class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ('user', 'group')

    # Get query set for the post then filter by username
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))

# Create a post
class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('message', 'group')
    model = models.Post

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

# Delete a post
class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ('user', 'group')
    success_url = reverse_lazy('posts:all')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id = self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Post Deleted')
        return super().delete(*args, **kwargs)
