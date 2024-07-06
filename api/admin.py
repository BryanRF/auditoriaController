from django.contrib import admin
from .models import *

# Registrar los modelos en el panel de administración
admin.site.register(Auditor)
admin.site.register(Estado)
admin.site.register(EntidadAuditada)
admin.site.register(InformeAuditoria)
admin.site.register(AreaSeguridad)
admin.site.register(SeccionAuditoria)
admin.site.register(Persona)
