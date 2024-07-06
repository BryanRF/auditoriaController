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
    motivo = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Informe de Auditoría - {self.fecha} - {self.entidad_auditada} -{self.motivo}"
    
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

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=8)
    rol = models.CharField(max_length=120, blank=True, null=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre
# Modelo para cada sección de la auditoría
class SeccionAuditoria(models.Model):
    informe = models.ForeignKey(InformeAuditoria, on_delete=models.CASCADE)
    area_seguridad = models.ForeignKey(AreaSeguridad, on_delete=models.CASCADE)
    codigo_referencia = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Unique para asegurar la unicidad
    descripcion_control = models.TextField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    evidencia = models.FileField(upload_to='', blank=True, null=True)  # Campo opcional
    observaciones = models.TextField(blank=True, null=True)  # Campo opcional
    recomendaciones = models.TextField(blank=True, null=True)  # Campo opcional
    pregunta = models.TextField(blank=True, null=True)  # Nuevo campo para la pregunta
    respuesta = models.TextField(blank=True, null=True)  # Nuevo campo para la respuesta
    quien_responde = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='secciones_responsables', blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.codigo_referencia:  # Generar código de referencia si no se proporciona
            palabras = self.area_seguridad.descripcion.split()
            letras = ''.join([palabra[0] for palabra in palabras if palabra.lower() not in ['de', 'la','en','el']])
            # Lógica para generar el código autoincrementable, por ejemplo:
            last_code = SeccionAuditoria.objects.order_by('-id').first()
            if last_code:
                last_id = int(last_code.codigo_referencia.split('-')[-1]) + 1
                self.codigo_referencia = f"{letras.upper()}-{last_id:03}"
            else:
                self.codigo_referencia = f"{letras.upper()}-001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_referencia} -{self.estado.descripcion}- {self.area_seguridad} - {self.pregunta}"
