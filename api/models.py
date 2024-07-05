from django.db import models

# Modelo para los auditores
class Auditor(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=8)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo para la entidad auditada
class EntidadAuditada(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField()
    responsable = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo para el informe de auditoría
class InformeAuditoria(models.Model):
    fecha = models.DateField(auto_now_add=True)
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE)
    entidad_auditada = models.ForeignKey(EntidadAuditada, on_delete=models.CASCADE)

    def __str__(self):
        return f"Informe de Auditoría - {self.fecha}"
    
class Estado(models.Model):
    descripcion = models.CharField(max_length=200)
    color = models.CharField(max_length=50)
    icono = models.CharField(max_length=50)

    def __str__(self):
        return f"Estado - {self.descripcion}"
    
# Modelo para el área de seguridad
class AreaSeguridad(models.Model):
    descripcion = models.CharField(max_length=200)
    def __str__(self):
        return self.descripcion

# Modelo para cada sección de la auditoría
class SeccionAuditoria(models.Model):
    informe = models.ForeignKey(InformeAuditoria, on_delete=models.CASCADE)
    area_seguridad = models.ForeignKey(AreaSeguridad, on_delete=models.CASCADE)
    codigo_referencia = models.CharField(max_length=20)
    descripcion_control = models.TextField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    evidencia = models.FileField(upload_to='media/')
    observaciones = models.TextField()
    recomendaciones = models.TextField()

    def __str__(self):
        return f"{self.codigo_referencia} - {self.area_seguridad}"
