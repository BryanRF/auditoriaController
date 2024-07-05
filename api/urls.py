from django.urls import path
from .views import GenerarInformePDF

urlpatterns = [
    # Otras URLs de tu aplicación
    path('generar-informe/', GenerarInformePDF.as_view(), name='generar-informe-pdf'),
]
