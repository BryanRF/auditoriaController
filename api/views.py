from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY,TA_RIGHT
from .models import SeccionAuditoria, InformeAuditoria
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from django.views import View
import openpyxl
from collections import Counter
from django.http import HttpResponse
from django.views import View
from .models import SeccionAuditoria
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side
from io import BytesIO
from .models import SeccionAuditoria

class ExportarAuditoriaExcel(View):
    def get(self, request, *args, **kwargs):
        # Crear un nuevo libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Auditoría General"

        # Establecer los encabezados de la tabla
        encabezados = ['Código', 'Área de Seguridad', 'Descripción del Control', 'Estado', 'Pregunta', 'Respuesta', 'Observaciones', 'Recomendaciones']
        ws.append(encabezados)

        # Ajustar el tamaño de las columnas y centrar el texto
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter  # Obtiene la letra de la columna
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width
            for cell in col:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        # Obtener los datos de SeccionAuditoria
        queryset = SeccionAuditoria.objects.all()

        # URL base del servidor donde se almacenan las evidencias
        base_url = request.build_absolute_uri('/')[:-1]

        # Agregar los datos al Excel
        for seccion in queryset:
            evidencia_url = base_url + seccion.evidencia.url if seccion.evidencia else 'Sin evidencia'
            fila = [
                seccion.codigo_referencia,
                seccion.area_seguridad.descripcion,
                seccion.descripcion_control,
                seccion.estado.descripcion,
                seccion.pregunta,
                seccion.respuesta,
                seccion.observaciones,
                seccion.recomendaciones,
            ]
            ws.append(fila)

        # Crear un borde para las celdas
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))

        # Aplicar el borde a todas las celdas
        for row in ws.iter_rows():
            for cell in row:
                cell.border = thin_border

        # Crear un objeto BytesIO para almacenar el archivo Excel
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Preparar la respuesta HTTP con el archivo Excel
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Informe_Auditoria_General.xlsx'

        return response
    
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

        # Obtener el primer informe asociado para los detalles generales
        informe = queryset.first().informe if queryset.exists() else None
        auditor = informe.auditor if informe else None
        entidad_auditada = informe.entidad_auditada if informe else None

        # URL base del servidor donde se almacenan las evidencias
        base_url = request.build_absolute_uri('/')[:-1]

        # Datos para cada sección del informe
        datos_secciones = []
        for seccion in queryset:
            datos_secciones.append({
                'codigo_referencia': seccion.codigo_referencia,
                'area_seguridad': seccion.area_seguridad.descripcion,
                'descripcion_control': seccion.descripcion_control,
                'estado': seccion.estado.descripcion,
                'evidencia': base_url + seccion.evidencia.url if seccion.evidencia else '',
                'observaciones': seccion.observaciones,
            })

        # Función para generar una tabla con los datos proporcionados
        def generar_tabla_informacion_general(datos):
            # Estilos para los párrafos y encabezados
            styles = getSampleStyleSheet()
            estilo_parrafo = styles['BodyText']

            # Estilo de párrafo justificado
            estilo_justificado = ParagraphStyle(name='Justify', parent=estilo_parrafo, alignment=TA_JUSTIFY)

            # Encabezados de la tabla
            encabezados = ['Código', 'Área de Seguridad', 'Descripción del Control',  'Estado', 'Evidencia', 'Observaciones',]

            # Datos de la tabla
            datos_tabla = [encabezados]
            i=1
            for seccion in datos:
                if seccion['evidencia']:
                    evidencia = Paragraph(f'<a target="_blank" href="{seccion["evidencia"]}" color="blue"><b>[ANEXO {i}]</b></a>', estilo_parrafo)
                else:
                    evidencia = "Sin evidencia"
                fila = [
                    Paragraph(seccion['codigo_referencia'], estilo_justificado),
                    Paragraph(seccion['area_seguridad'], ),
                    Paragraph(seccion['descripcion_control'], estilo_justificado),
                    Paragraph(seccion['estado'], estilo_justificado),
                    evidencia,
                    Paragraph(seccion['observaciones'], estilo_justificado),
                ]
                i+= 1
                datos_tabla.append(fila)

            # Crear la tabla
            tabla = Table(datos_tabla, colWidths=[80, 120, 180, 70, 120, 180])

            # Estilo de la tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('WORDWRAP', (0, 1), (-1, -1), 1),
            ])
            tabla.setStyle(estilo_tabla)

            return tabla

        # Función para generar la tabla de detalles de la auditoría en horizontal
        def generar_tabla_detalles_auditoria():
            # Estilos para los párrafos y encabezados
            styles = getSampleStyleSheet()
            estilo_parrafo = styles['BodyText']

            # Estilo de párrafo justificado
            estilo_justificado = ParagraphStyle(name='Justify', parent=estilo_parrafo, alignment=TA_JUSTIFY)

            # Detalles del informe
            detalles_informe = [
                ['Entidad Auditada', entidad_auditada.nombre],
                ['Dirección', entidad_auditada.direccion],
                ['Responsable', entidad_auditada.responsable],
                ['Auditor(es)', auditor.nombre],
                ['DNI del Auditor', auditor.dni],
                ['Email del Auditor', auditor.email],
                ['Teléfono del Auditor', auditor.telefono],
                ['Fecha del Informe', informe.fecha.strftime('%d/%m/%Y')],
                # ['Motivo de la Auditoría', informe.motivo]
                [Paragraph('Motivo de la Auditoría', styles['BodyText']), Paragraph(informe.motivo, styles['BodyText'])],
            ]

            # Crear la tabla
            tabla_detalles = Table(detalles_informe, colWidths=[150, '*'])

            # Estilo de la tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('WORDWRAP', (0, 1), (-1, -1), 1),
            ])
            tabla_detalles.setStyle(estilo_tabla)

            return tabla_detalles
        def generar_tablas_secciones(datos_secciones,pos, styles):
            # Lista para almacenar todas las tablas
            tablas_secciones = []
         
            # Recorrer cada sección y crear una tabla vertical
            for seccion in datos_secciones:
                tabla_seccion = Table([
                    [Paragraph('Código', styles['BodyText']), Paragraph(seccion['codigo_referencia'], styles['BodyText'])],
                    [Paragraph('Área de Seguridad', styles['BodyText']), Paragraph(seccion['area_seguridad'], styles['BodyText'])],
                    [Paragraph('Descripción del Control', styles['BodyText']), Paragraph(seccion['descripcion_control'], styles['BodyText'])],
                    [Paragraph('Estado', styles['BodyText']), Paragraph(seccion['estado'], styles['BodyText'])],
                    [Paragraph('Evidencia', styles['BodyText']), Paragraph(f'<a target="_blank" href="{seccion["evidencia"]}" color="blue"><b>[ANEXO {pos}]</b></a>', styles['BodyText']) if seccion['evidencia'] else ''],
                    [Paragraph('Observaciones', styles['BodyText']), Paragraph(seccion['observaciones'], styles['BodyText'])],
                    [Paragraph('Recomendaciones', styles['BodyText']), Paragraph(seccion['recomendaciones'], styles['BodyText'])],
                ], colWidths=[150, '*'])
                
                # Agregar estilo a la tabla
                tabla_seccion.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ]))

                tablas_secciones.append(tabla_seccion)
        
            return tablas_secciones
        # Función principal para generar el PDF
        def generar_tabla_resumen(datos_secciones):
            # Contar los estados de las secciones
            print(datos_secciones)
            estados = [seccion['estado'] for seccion in datos_secciones]
            contador_estados = Counter(estados)

            # Calcular el número total de controles auditados
            numero_total_controles = len(datos_secciones)

            # Obtener el número de controles cumplidos y no cumplidos
            numero_controles_cumplidos = contador_estados.get('Cumple', 0)
            numero_controles_no_cumplidos = contador_estados.get('No Cumple', 0)

            # Calcular el porcentaje de cumplimiento
            if numero_total_controles > 0:
                porcentaje_cumplimiento = f"{(numero_controles_cumplidos / numero_total_controles) * 100:.2f}%"
            else:
                porcentaje_cumplimiento = "0%"

            # Acciones correctivas recomendadas

            # Datos del resumen de resultados
            datos_resumen = [
                ['Número Total de Controles Auditados', str(numero_total_controles)],
                ['Número de Controles Cumplidos', str(numero_controles_cumplidos)],
                ['Número de Controles No Cumplidos', str(numero_controles_no_cumplidos)],
                ['Porcentaje de Cumplimiento', porcentaje_cumplimiento],
            ]

            # Crear la tabla
            tabla_resumen = Table(datos_resumen, colWidths=[250, '*'])

            # Estilo de la tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ])
            tabla_resumen.setStyle(estilo_tabla)

            return tabla_resumen
    
        def generar_pdf(datos_secciones):
            # Nombre del archivo de salida
            nombre_archivo = "Informe_Auditoria.pdf"
            styles = getSampleStyleSheet()
            estilo_titulo = styles['Heading2']
            estilo_subtitulo = styles['Heading4']
            estilo_parrafo = styles['BodyText']

            # Configuración del documento PDF
            doc = SimpleDocTemplate(nombre_archivo, pagesize=landscape(letter))

            # Contenido del PDF
            contenido = []

            # Título del informe
            titulo = Paragraph("Plan de Auditoría de Seguridad en TI para el Área de Desarrollo de Software", estilo_titulo)
            contenido.append(titulo)
            
            # Introducción
            introduccion = Paragraph(
                "<b>Introducción</b><br/><br/>"
                "La auditoría de seguridad en TI tiene como objetivo evaluar y mejorar las medidas de seguridad implementadas "
                "en el área de desarrollo de software, asegurando la protección de los datos y el cumplimiento de las políticas "
                "de seguridad. Este plan de auditoría se enfoca en revisar el control de acceso, la protección de datos, la "
                "gestión de vulnerabilidades y la adherencia a las políticas de desarrollo seguro, considerando las diferentes "
                "jerarquías y roles dentro del equipo de trabajo.",
                estilo_parrafo
            )
            introduccion.alignment = TA_JUSTIFY  # Asegurar que el párrafo esté justificado
            contenido.append(introduccion)

            # Espacio
            contenido.append(Spacer(1, 12))

            # Tabla de Información General con título "Detalles de la Auditoría"
            contenido.append(Paragraph("Detalles de la Auditoría", estilo_subtitulo))
            tabla_detalles_auditoria = generar_tabla_detalles_auditoria()
            contenido.append(tabla_detalles_auditoria)
            
            # Espacio entre tablas
            contenido.append(Spacer(1, 24))
            contenido.append(Paragraph("Resumen Auditoria", estilo_subtitulo))
            tabla_resumen = generar_tabla_resumen(datos_secciones)
            contenido.append(tabla_resumen)
            # Espacio entre tablas
            contenido.append(Spacer(1, 24))

            # Nueva página para la tabla de detalles de la auditoría en horizontal
            contenido.append(PageBreak())
            contenido.append(Paragraph("Auditoria General", estilo_subtitulo))
            tabla_informacion_general = generar_tabla_informacion_general(datos_secciones)
            contenido.append(tabla_informacion_general)
            datos_secciones = []
            contenido.append(PageBreak())
            contenido.append(Paragraph("Detalles de Auditoría por Sección", estilo_subtitulo))
            contador_tablas = 0
            pos=1
            for seccion in queryset:
                datos_seccion = {
                    'codigo_referencia': seccion.codigo_referencia,
                    'area_seguridad': seccion.area_seguridad.descripcion,
                    'descripcion_control': seccion.descripcion_control,
                    'estado': seccion.estado.descripcion,
                    'evidencia': base_url + seccion.evidencia.url if seccion.evidencia else '',
                    'observaciones': seccion.observaciones,
                    'recomendaciones': seccion.recomendaciones,
                }
                
                # Generar las tablas para la sección actual
                tablas_secciones = generar_tablas_secciones([datos_seccion],pos, styles)
                pos += 1
                
                # Agregar cada tabla al contenido del PDF
                for tabla in tablas_secciones:
                    # Verificar si es necesario añadir un salto de página
                    if contador_tablas > 0 and contador_tablas % 2 == 0:
                        contenido.append(PageBreak())
                    contenido.append(tabla)
                    contenido.append(Spacer(1, 12))

                    # Incrementar el contador de tablas
                    contador_tablas += 1
            
            querysets = SeccionAuditoria.objects.all()
            datos_secciones = []
            for seccion in querysets:
                datos_secciones.append({
                    'codigo_referencia': seccion.codigo_referencia,
                    'area_seguridad': seccion.area_seguridad.descripcion,
                    'descripcion_control': seccion.descripcion_control,
                    'estado': seccion.estado.descripcion,
                    'evidencia': base_url + seccion.evidencia.url if seccion.evidencia else '',
                    'observaciones': seccion.observaciones,
                })
            # contenido.append(PageBreak())
            
            # Generar el PDF
            doc.build(contenido)

            return nombre_archivo

        # Generar el PDF y devolverlo como respuesta HTTP
        pdf_generado = generar_pdf(datos_secciones)
        with open(pdf_generado, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_generado}"'
        return response
    
class GenerarCuestionarioPDF(View):
    def get(self, request, *args, **kwargs):
        # Obtener todos los datos de SeccionAuditoria ordenados por área de seguridad
        queryset = SeccionAuditoria.objects.all().order_by('-area_seguridad__descripcion')

        # Crear el documento PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Cuestionario.pdf"'

        # Configurar el tamaño y los estilos
        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()

        # Contenido del PDF
        contenido = []
        # Obtener el primer informe asociado para los detalles generales
        informe = queryset.first().informe if queryset.exists() else None
        entidad_auditada = informe.entidad_auditada if informe else None
        # Título del cuestionario
        titulo = Paragraph(f'Cuestionario de Auditoría de Seguridad de TI en {entidad_auditada}', styles['Title'])
        contenido.append(titulo)
        contenido.append(Spacer(1, 9))
        fecha = informe.fecha.strftime('%d/%m/%Y')
        descripcion = Paragraph(f'El cuestionario fue formulado por <b>{informe.auditor.nombre}</b> y auditado por su grupo académico el <b>{fecha}</b>.', styles['BodyText'])
        contenido.append(descripcion)
        contenido.append(Spacer(1, 9))
        
        # Variables para guardar el área de seguridad actual y sus preguntas
        area_actual = None
        preguntas_area = []

        # Iterar sobre cada sección de la auditoría
        for seccion in queryset:
            # Verificar si cambia el área de seguridad
            if seccion.area_seguridad != area_actual:
                # Agregar las preguntas del área anterior, si hay alguna
                if preguntas_area:
                    contenido.extend(self._generar_seccion(area_actual, preguntas_area, styles))
                    contenido.append(Spacer(1, 9))
                    preguntas_area = []  # Reiniciar la lista de preguntas

                # Actualizar el área de seguridad actual
                area_actual = seccion.area_seguridad

            # Agregar la pregunta actual a la lista
            preguntas_area.append(seccion)

        # Agregar la última sección
        if preguntas_area:
            contenido.extend(self._generar_seccion(area_actual, preguntas_area, styles))
        
        # Separador final y firmas
        contenido.append(Spacer(1, 0.5 * inch))
        firmas = [
                ["_________________________", "_________________________"],
                ["Nombre y firma", "Nombre y firma"],
                ["Auditor", f'Responsable de {entidad_auditada}'],
            ]
        table = Table(firmas)
        table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10)
            ]))
        contenido.append(table)
        contenido.append(Spacer(1, 0.5 * inch))
        powered_by = f"Powered by Grupo7 - 2024 ®"
        contenido.append(Paragraph(powered_by, styles['Normal']))

        # Construir el PDF
        doc.build(contenido)
        return response

    def _generar_seccion(self, area_seguridad, preguntas, styles):
        # Función interna para generar una sección del PDF para un área de seguridad específica
        contenido_seccion = []

        # Título del área de seguridad
        contenido_seccion.append(Paragraph(f"<b>{area_seguridad.descripcion}</b>", styles['Heading2']))
        contenido_seccion.append(Spacer(1, 6))
        justified_style = ParagraphStyle(
            name='Justified',
            parent=styles['BodyText'],
            alignment=TA_JUSTIFY
        )
        # Iterar sobre cada pregunta en el área de seguridad
        for idx, seccion in enumerate(preguntas, start=1):
            contenido_seccion.append(Paragraph(f"<b>{seccion.codigo_referencia}</b>. {seccion.pregunta}", justified_style))
            contenido_seccion.append(Spacer(1, 3))
            contenido_seccion.append(Paragraph(f"{seccion.respuesta} <b>({seccion.quien_responde.nombre})</b>", justified_style))
            contenido_seccion.append(Spacer(1, 9))

        return contenido_seccion