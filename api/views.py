from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import SeccionAuditoria  # Asegúrate de importar tu modelo de auditoría
from django.views import View
from django.utils import timezone

class GenerarInformePDF(View):
    def get(self, request, *args, **kwargs):
        # Obtener los parámetros de filtro de la solicitud GET
        entidad = request.GET.get('entidad', None)
        fecha = request.GET.get('fecha', None)

        # Filtrar los datos según los parámetros recibidos
        queryset = SeccionAuditoria.objects.all()
        if entidad:
            queryset = queryset.filter(informe__entidad_auditada__nombre__icontains=entidad)
        if fecha:
            queryset = queryset.filter(informe__fecha=fecha)

        # Datos para cada sección del informe
        datos_secciones = []
        for seccion in queryset:
            datos_secciones.append({
                'codigo_referencia': seccion.codigo_referencia,
                'area_seguridad': seccion.area_seguridad.descripcion,
                'descripcion_control': seccion.descripcion_control,
                'estado': seccion.estado,
                'evidencia': seccion.evidencia.url if seccion.evidencia else '',
                'observaciones': seccion.observaciones,
                'recomendaciones': seccion.recomendaciones
            })

        # Función para generar una tabla con los datos proporcionados
        def generar_tabla(datos):
            # Estilos para los párrafos y encabezados
            styles = getSampleStyleSheet()
            estilo_titulo = styles['Heading2']
            estilo_parrafo = styles['BodyText']

            # Encabezados de la tabla
            encabezados = ['Código de Referencia', 'Área de Seguridad', 'Descripción del Control', 
                           'Estado', 'Evidencia', 'Observaciones', 'Recomendaciones']

            # Datos de la tabla
            datos_tabla = [encabezados]
            for seccion in datos:
                fila = [
                    seccion['codigo_referencia'],
                    seccion['area_seguridad'],
                    seccion['descripcion_control'],
                    seccion['estado'],
                    seccion['evidencia'],
                    seccion['observaciones'],
                    seccion['recomendaciones']
                ]
                datos_tabla.append(fila)

            # Crear la tabla
            tabla = Table(datos_tabla, colWidths=[80, 120, 180, 70, 120, 120, 180])

            # Estilo de la tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ])
            tabla.setStyle(estilo_tabla)

            return tabla

        # Función principal para generar el PDF
        def generar_pdf(datos_secciones):
            # Nombre del archivo de salida
            nombre_archivo = "Informe_Auditoria.pdf"
            styles = getSampleStyleSheet()
            estilo_titulo = styles['Heading2']
            estilo_parrafo = styles['BodyText']
            # Configuración del documento PDF
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)

            # Contenido del PDF
            contenido = []

            # Título del informe
            titulo = Paragraph("Informe de Auditoría de Seguridad", estilo_titulo)
            contenido.append(titulo)

            # Generar tablas para cada sección
            tabla_secciones = generar_tabla(datos_secciones)
            contenido.append(tabla_secciones)

            # Generar el PDF
            doc.build(contenido)

            return nombre_archivo

        # Generar el PDF y devolverlo como respuesta HTTP
        pdf_generado = generar_pdf(datos_secciones)
        with open(pdf_generado, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_generado}"'
        return response
