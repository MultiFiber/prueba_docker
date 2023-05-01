from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'client', views.ClientView,'client')
router.register(r'os', views.OsView, 'os')
router.register(r'ospic', views.OsPicView,  'ospic')
router.register(r'displacement', views.DisplacementView, 'displacement')
router.register(r'dashboard', views.DashboardView,  'dashboard')

urlpatterns = [
    path('v1/get_plans/brujula/', views.GetBrujulaPlanView.as_view()),
    path('v1/get_plans/oraculo/', views.GetOraculoPlanView.as_view()),
    path('v1/os/choices/', views.OsFormChoicesList.as_view(), name="os-form-choices"),
    path('v1/excel_route_report/', views.ExcelRouteReportView.as_view(), name="excel_route_report"),
    path('v1/reschedule_os/', views.RescheduleOSView.as_view(), name='reschedule_os'),
    path('v1/calendar_os/', views.CalendarOsView.as_view(), name='calendar_os'),
    path('v1/journeys_traveled/', views.JourneysTraveledView.as_view(), name='journeys_traveled'),    
    path('v1/start_finish_reroute/', views.StartAndFinishRerouteView.as_view(), name='start_finish_reroute'),    
    path('v1/trip_summary/', views.TripSummaryView.as_view(), name='trip_summary'),
    path('v1/report/PDF', views.ReportView.as_view(), name='report_'),
    path('v1/dashboard-PDF/', views.PDFDashboardView.as_view(), name='dashboard_pdf'),
    path('v1/OS_listing_search_engine/', views.OsListingSearchEngineView.as_view(), name='os_listing_search_engine'),
    path('v1/route_report-PDF/', views.PDFRouteReportView.as_view(), name='route_report_pdf'),
    path('v1/tour_summary/', views.GetTourSummary.as_view(), name='tour_summary'),
    path('v1/', include(router.urls)),
]
