"""URL-маршруты приложения. re_path используется для требований по регулярным выражениям."""
from django.urls import path, re_path

from core import views
from core.views import RealtyLoginView, RealtyLogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news_list, name='news'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),
    path('faq/', views.faq_list, name='faq'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('reviews/add/', views.review_create, name='review_add'),
    path('promos/', views.promos, name='promos'),
    path('catalog/', views.catalog, name='catalog'),
    path('api-demo/', views.api_demo, name='api_demo'),
    path('register/', views.register_view, name='register'),
    path('login/', RealtyLoginView.as_view(), name='login'),
    path('logout/', RealtyLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/create/', views.property_create, name='property_create'),
    re_path(r'^properties/(?P<pk>\d+)/$', views.property_detail, name='property_detail'),
    re_path(r'^properties/(?P<pk>\d+)/buy/$', views.purchase_property, name='property_buy'),
    re_path(r'^properties/(?P<pk>\d+)/edit/$', views.property_update, name='property_update'),
    re_path(r'^properties/(?P<pk>\d+)/delete/$', views.property_delete, name='property_delete'),
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    re_path(r'^sales/(?P<pk>\d+)/edit/$', views.sale_update, name='sale_update'),
    re_path(r'^sales/(?P<pk>\d+)/delete/$', views.sale_delete, name='sale_delete'),
    path('statistics/', views.statistics_view, name='statistics'),
    re_path(r'^api/sales/?$', views.api_sales_json, name='api_sales'),
]
