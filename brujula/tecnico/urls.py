from django.urls import path, include
from rest_framework import routers
from . import views, views_calendar

router = routers.DefaultRouter()
router.register(r'technician', views.TechnicianView, 'Technician')
router.register(r'technicianpic', views.TechnicianPicView, 'technicianpic')
router.register(r'schedule', views.ScheduleView, 'schedule')
router.register(r'disponibility', views.DisponibilityView, 'disponibility')
router.register(r'absence', views.AbsenceView, 'Absence'),
router.register(r'holiday', views.HolidayView, 'Holiday'),


urlpatterns = [
    path('v1/technician/choices/', views.TechnicianFormChoicesList.as_view(), name="technician-form-choices"), 
    path('v1/absence_finder/', views.AbsenceFinderView.as_view(), name="absence_finder"), 
    path('v1/absence_create/', views.AbsenceCreatorView.as_view(), name="absence_creator"), 
    path('v1/calendar_technician/', views_calendar.CalendarTechnicianView.as_view(), name='calendar_os'),
    path('v1/calendar_technician_app/', views_calendar.CalendarTechnicianAppView.as_view(), name='calendar_os'),
    path('v1/available_hours/', views_calendar.RangeOfHoursAvailableView.as_view(), name='available_hours'),
    path('v1/create_segmented_availability/', views_calendar.CreateSegmentedAvailabilityView.as_view(), name='create_segmented_availability'), 
    path('v1/available_technicians/', views_calendar.ListOfAvailableTechniciansView.as_view(), name='available_technicians'),
    path('v1/modify_category_technician/', views.ModifyCategoriesInDatatableView.as_view(), name='modify_category'),
    path('v1/create_disponibility/', views.CreateDisponibilityScheduleView.as_view(), name='create_disponibility'),
    path('v1/', include(router.urls)),
]