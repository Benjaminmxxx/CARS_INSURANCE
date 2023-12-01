
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_pdf(result,max_sin,min_sin,max_sines,max_prom_sev,min_sines,min_prom_sev,rango_mayor,rango_menor,rango_prom_mayor,rango_prom_menor, output_filename='informe.pdf'):
    # Configurar el tamaño de la página (puedes cambiarlo según tus necesidades)
    width, height = letter

    # Crear el objeto PDF
    pdf_canvas = canvas.Canvas(output_filename, pagesize=letter)
    
    # Configurar el título del informe
    title = "Informe de Resultados"
    pdf_canvas.setFont("Helvetica", 16)
    pdf_canvas.drawString(width / 2 - pdf_canvas.stringWidth(title, "Helvetica", 16) / 2, height - 50, title)

    # Agregar datos al informe
    pdf_canvas.setFont("Helvetica", 12)
    y_position = height - 80
    
    #Siniestralidad Mensual de la compañía
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "1.-Siniestralidad Mensual de la compañía:")
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)
    for index in result.index:
    # Imprimir el índice
        pdf_canvas.drawString(100, y_position, f"{index}")
    # Imprimir la Siniestralidad_Mensual al lado del índice
        pdf_canvas.drawString(200, y_position, f"{result.loc[index, 'Siniestralidad_Mensual']}")
        y_position -= 20

    # Agregar una imagen al informe (reemplaza 'ruta_de_la_imagen' con la ruta de tu imagen)
    imagen_path = 'Siniestralidad_Mensual.png'
    pdf_canvas.drawInlineImage(imagen_path, 100, height - 400, width=400, height=200)

    y_position = height - 440
    #Cobertura con mayor cantidad de siniestros
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "2.-Cobertura con Mayor Cantidad de Siniestros:")
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)
    # Agregar título para los resultados en paralelo
    pdf_canvas.drawString(100, y_position, "Nombre")
    pdf_canvas.drawString(170, y_position, "Descripción")
    pdf_canvas.drawString(260, y_position, "No. Siniestros")
    y_position -= 20
    for index, row in max_sin.iterrows():
        pdf_canvas.drawString(100, y_position, f"{row['name']}")
        pdf_canvas.drawString(150, y_position, f"{row['description_y']}")
        pdf_canvas.drawString(280, y_position, f"{row['Siniestros']}")
        y_position -= 30
    
    y_position = height - 510
    #Cobertura con menor cantidad de siniestros
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "2.2.-Cobertura con Menor Cantidad de Siniestros:")
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)
    # Agregar título para los resultados en paralelo
    pdf_canvas.drawString(100, y_position, "Nombre")
    pdf_canvas.drawString(170, y_position, "Descripción")
    pdf_canvas.drawString(260, y_position, "No. Siniestros")
    y_position -= 20
    for index, row in min_sin.iterrows():
        pdf_canvas.drawString(100, y_position, f"{row['name']}")
        pdf_canvas.drawString(170, y_position, f"{row['description_y']}")
        pdf_canvas.drawString(280, y_position, f"{row['Siniestros']}")
        y_position -= 30
    
    # Agregar una imagen al informe (reemplaza 'ruta_de_la_imagen' con la ruta de tu imagen)
    imagen_path = 'Siniestros.png'
    pdf_canvas.drawInlineImage(imagen_path, 100, height - 760, width=400, height=200)

    pdf_canvas.showPage()

    y_position = height - 100

     #Mayor Siniestralidad por Partner
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "3.-Partner con mayor siniestralidad:")
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)
    for index in max_sines.index:
    # Imprimir el índice
        pdf_canvas.drawString(100, y_position, f"{index}")
    # Imprimir la Siniestralidad_Mensual al lado del índice
        pdf_canvas.drawString(200, y_position, f"{max_sines.loc[index, 'amount']}")
        y_position -= 20
    
        y_position = height - 140
    #Severidad Promedio para el partner con mayor Siniestralidad
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "Promedio de severidad:")
    pdf_canvas.setFont("Helvetica", 12)
    y_position -= 20
    for index, row in max_prom_sev.iterrows():
        pdf_canvas.drawString(100, y_position, f"{row['policy_number']}")
        pdf_canvas.drawString(170, y_position, f"{row['amount']}")
        y_position -= 30
    
    y_position = height - 200
    #Menor Siniestralidad por Partner
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "3.1.-Partner con menor siniestralidad:")
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)
    for index in min_sines.index:
    # Imprimir el índice
        pdf_canvas.drawString(100, y_position, f"{index}")
    # Imprimir la Siniestralidad_Mensual al lado del índice
        pdf_canvas.drawString(200, y_position, f"{min_sines.loc[index, 'amount']}")
        y_position -= 30
    
        y_position = height - 250
    #Severidad Promedio para el partner con menor Siniestralidad
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "Promedio de severidad:")
    pdf_canvas.setFont("Helvetica", 12)
    y_position -= 20
    for index, row in min_prom_sev.iterrows():
        pdf_canvas.drawString(100, y_position, f"{row['policy_number']}")
        pdf_canvas.drawString(170, y_position, f"{row['amount']}")
        y_position -= 30
    
    # Agregar una imagen al informe (reemplaza 'ruta_de_la_imagen' con la ruta de tu imagen)
    imagen_path = 'Siniestralidad_Partner.png'
    pdf_canvas.drawInlineImage(imagen_path, 100, height - 500, width=400, height=200)

    imagen_path = 'Siniestralidad_Promedio_Partner.png'
    pdf_canvas.drawInlineImage(imagen_path, 100, height - 700, width=400, height=200)

    pdf_canvas.showPage()

    y_position = height - 80
    
    #Rango etario 
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, f"4.-Rangos Etarios con mayor y menor cantidad de usuarios:")
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(100, y_position, f"Rango etario mayor : {(rango_mayor)}")
    y_position -= 20
    pdf_canvas.drawString(100, y_position, f"Rango etario menor: {(rango_menor)}")
    
    imagen_path = 'RangoEtario.png'
    pdf_canvas.drawInlineImage(imagen_path, 100, height - 350, width=400, height=200)
    
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)

    y_position = height - 380
    #Severidad Promedio para el partner con menor Siniestralidad
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, y_position, "4.1.-Promedio de severidad:")
    y_position -= 20
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(100, y_position, f"Rango etario mayor : {(rango_prom_mayor)}")
    y_position -= 20
    pdf_canvas.drawString(100, y_position, f"Rango etario menor: {(rango_prom_menor)}")
    y_position -= 20

    y_position = height - 500
    
    imagen_path = 'Severidad_Etario.png'
    pdf_canvas.drawInlineImage(imagen_path, 100, height - 650, width=400, height=200)
    
    # Guardar el PDF
    pdf_canvas.save()