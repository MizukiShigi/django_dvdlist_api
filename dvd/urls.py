# router = routers.SimpleRouter()
# router.register(r'dvd', )

from django.urls import path
from .views import DvdListView, CategoryView, LanguageView, RentalView, GetPostAPI
from django.conf.urls import url

urlpatterns = [
    url(r'dvdlist/', DvdListView.as_view()),
    url(r'categorylist/', CategoryView.as_view()),
    url(r'languagelist/', LanguageView.as_view()),
    url(r'rental/', RentalView.as_view()),
    path('<int:pk>/', GetPostAPI.as_view()),
]