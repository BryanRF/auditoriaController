from rest_framework import serializers
from .models import InformeAuditoria

class InformeAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeAuditoria
        fields = ['id', 'fecha', 'auditor', 'entidad_auditada']
