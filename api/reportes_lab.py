from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

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
def generar_pdf():
    # Nombre del archivo de salida
    nombre_archivo = "Informe_Auditoria.pdf"

    # Configuración del documento PDF
    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)

    # Contenido del PDF
    contenido = []

    # Título del informe
    titulo = Paragraph("Informe de Auditoría de Seguridad", estilo_titulo)
    contenido.append(titulo)

    # Generar tablas para cada sección
    tabla_evaluacion_accesos = generar_tabla(evaluacion_accesos)
    contenido.append(tabla_evaluacion_accesos)

    # Puedes seguir agregando más tablas para las otras secciones aquí

    # Generar el PDF
    doc.build(contenido)

# Llamar a la función para generar el PDF
generar_pdf()
