from django.urls import path
from .views import GenerarInformePDF
from .views import GenerarCuestionarioPDF

urlpatterns = [
    # Otras URLs de tu aplicación
    path('generar-informe/', GenerarInformePDF.as_view(), name='generar-informe-pdf'),
    path('generar-questionario/', GenerarCuestionarioPDF.as_view(), name='generar-questionario-pdf'),
]
