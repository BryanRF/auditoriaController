from django.contrib import admin
from .models import Auditor, EntidadAuditada, InformeAuditoria, AreaSeguridad, SeccionAuditoria

# Registrar los modelos en el panel de administración
admin.site.register(Auditor)
admin.site.register(EntidadAuditada)
admin.site.register(InformeAuditoria)
admin.site.register(AreaSeguridad)
admin.site.register(SeccionAuditoria)
