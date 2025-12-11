"""
URL configuration for hatchery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from cmr import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_view, name='landing page'),
    path('accounts/', include('allauth.urls')),
    path('about/', views.about_view, name='about'),
    path('spaces/<str:custom_id>/', views.dynamic_lookup_view, name='space-detail'),
    path('create/', views.space_create_view, name='create'),
    path("spaces/<str:custom_id>/reservations/", views.space_reservations_json, name="space-reservations-json"),
    #path('help/', help_view, name='help'),
    path('spaces/<str:custom_id>/delete/', views.space_delete_view, name='space-delete'),
    path('spaces/<str:custom_id>/reserve/', views.reservation_create_view, name='space-reserve'),
    path('spaces/', views.space_list_view, name='space-list'),
    path('spaces/<str:custom_id>/edit/', views.space_edit_view, name='space-edit'),
    path("spaces/<str:custom_id>/reservations/<int:reservation_id>/edit/", views.space_reservation_edit_view, name="space-reservation-edit"),
    path("spaces/<str:custom_id>/reservations/<int:reservation_id>/delete/", views.space_reservation_delete_view, name="space-reservation-delete"),
    path("reservations/my/", views.my_reservations_json, name="my-reservations-json"),
    path('reservations/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('reservations/delete/<int:reservation_id>/', views.delete_reservation, name='delete_reservation'),

    # staff adding machine
    path('machines/create/', views.New_machine_create_view, name='machine_create'),
    path("machines/existing/create/", views.Existing_machine_create_view, name="existing_machine_create"),
    path('machines/', views.machine_list_view, name='machine_list'),
    path("machines/<str:custom_id>/", views.machine_detail_view, name="machine-detail"),
    path("machines/<str:custom_id>/edit/", views.machine_edit_view, name="machine-edit"),
    path("machines/<str:custom_id>/delete/", views.machine_delete_view, name="machine-delete"),
    path('machines/<str:custom_id>/reserve/', views.reservation_create_viewMachines, name='machine-reserve'),
    path("machines/<str:custom_id>/reservations/", views.machines_reservations_json, name="machines-reservations-json"),
    path("machines/by-name/<str:name>/", views.machines_by_name_view, name="machine_by_name"),

    # Schedule management
    path('schedule/', views.schedule_list_view, name='schedule-list'),
    path('schedule/create/', views.schedule_create_view, name='schedule-create'),
    path('schedule/<int:id>/edit/', views.schedule_edit_view, name='schedule-edit'),
    path('schedule/<int:id>/delete/', views.schedule_delete_view, name='schedule-delete'),
    path('schedule/<int:id>/set-active/', views.schedule_set_active_view, name='schedule-set-active'),
    
    # Trainer
    path("trainers/", views.trainer_list_view, name="trainer_list"),
    path("trainers/create/", views.trainer_create_view, name="trainer_create"),
    path("trainers/all/reservations/", views.all_trainers_reservations_json, name="all-trainers-reservations-json"),
    path("trainers/<int:pk>/", views.trainer_detail_view, name="trainer_detail"),
    path("trainers/<int:pk>/edit/", views.trainer_edit_view, name="trainer_edit"),
    path("trainers/<int:pk>/delete/", views.trainer_delete_view, name="trainer_delete"),
    path("trainers/<int:pk>/reserve/", views.reservation_create_viewTrainers, name="trainer-reserve"),
    path("trainers/<int:pk>/reservations/", views.trainers_reservations_json, name="trainers-reservations-json"),
    path("trainers/<int:pk>/reservations/<int:reservation_id>/edit/", views.trainer_reservation_edit_view, name="trainer-reservation-edit"),
    path("trainers/<int:pk>/reservations/<int:reservation_id>/delete/", views.trainer_reservation_delete_view, name="trainer-reservation-delete"),
    path("trainers/<int:pk>/reservations/<int:reservation_id>/approve/", views.trainer_reservation_approve_view, name="trainer-reservation-approve"),

    # Help Tickets
    path('help/', views.help_ticket_list_view, name='help-ticket-list'),
    path('help/create/', views.help_ticket_create_view, name='help-ticket-create'),
    path('help/<int:ticket_id>/resolve/', views.help_ticket_resolve_view, name='help-ticket-resolve'),

    # Contacts
    path('contact/', views.contact_list_view, name='contact-list'),
    path('contact/create/', views.contact_create_view, name='contact-create'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)