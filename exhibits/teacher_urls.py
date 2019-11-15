from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.lessonPlanDirectory, name='lessonPlanDirectory'),    
    url(r'^(?P<lesson_id>\d+)/(?P<lesson_slug>[-\w]+)/$', views.lessonPlanView, name='lessonPlanView'),
    url(r'^(?P<lesson_id>\d+)/items/(?P<item_id>.+)/$', views.lessonPlanItemView, name='lessonPlanItemView'),
]