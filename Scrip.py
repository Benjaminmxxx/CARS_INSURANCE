import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from Informe import create_pdf
import warnings
warnings.filterwarnings("ignore")

claim=pd.read_excel('./Archivos/claim.xlsx')
service=pd.read_excel('./Archivos/service.xlsx')
status=pd.read_excel('./Archivos/status.xlsx')
status_type=pd.read_excel('./Archivos/status_type.xlsx')
status_cause=pd.read_excel('./Archivos/status_cause.xlsx')
people=pd.read_excel('./Archivos/people.xlsx')
dict_data=pd.read_excel('./Archivos/Diccionario de Datos.xlsx')

#Obtener una columna con la fecha de su 'updated_at'
def tiempo(archivo):
    archivo['updated_at'] = pd.to_datetime(archivo['updated_at'], errors='coerce')
    archivo['updated_day'] = archivo['updated_at'].dt.strftime('%Y-%m-%d').astype('period[D]')
    return archivo

#Aplicar función tiempo:
claim = tiempo(claim)
service = tiempo(service)
status = tiempo(status)
status_type = tiempo(status_type)
status_cause = tiempo(status_cause)
people = tiempo(people)

def buscar_y_actualizar(df_service, df_status, patrones, commercial_value, porcentaje_aumento):
    '''
    Función para modificar los valores in situ de la columna amount donde aplica cobertura 
    y el servicio aplica deductible, se ingresa tabla_service(df_service), después se deben 
    ingresar tipo de coberturas en una lista (patrones), se asigna el valor comercial del 
    auto a la variable commercial_value y se pone el porcentaje del deducible (porcentaje_aumento). 
    '''
    # Buscar por patrones en la columna 'description' de 'status'
    ids = []
    for patron in patrones:
        df_status['description'] = df_status['description'].fillna('')
        filtro = df_status['description'].str.contains(patron, case=False, regex=True)
        resultados = df_status[filtro].reset_index(drop=True)

        # Obtener id para filtrar las columnas en la tabla 'service'
        if not resultados.empty:
            coverage_id = resultados['id'][0]
            ids.append(coverage_id)

    # Filtrar las filas que cumplen con el deducible y las coberturas específicas en 'service_c'
    deducible_true_rows = df_service[(df_service['deductible'] == True) & (df_service['coverage_id'].isin(ids))]

    # Calcular el aumento en la columna 'amount'
    aumento = porcentaje_aumento * commercial_value
    df_service.loc[deducible_true_rows.index, 'amount'] += aumento

''' 
FLUJO CONSULTA 1: Siniestralidad mensual de la compañía

'''
#Copia para no alterar las tablas para los siguientes cálculos:
service_c=service.copy()

#Quitando servicios donde no hay "amount":
service_c.dropna(subset=['amount'], inplace=True)

#Sumando por mes el monto de gastos e ingresos. 
pd.options.display.float_format = '{:,.2f}'.format
result = service_c.groupby(service_c['updated_at'].dt.to_period("M")).agg({'amount': 'sum'})
#Incorporar la columna de prima devengada
result['primas_devengadas']=200000
#Calculo de la Siniestralidad_Mensual
result['Siniestralidad_Mensual']=result['amount']+result['primas_devengadas']
print('1.- Siniestralidad Mensual:\n',result)

'''-----------------------------------GRÁFICOS PARA EL REPORTE PDF----------------------------------'''
# Crear el gráfico de barras
plt.figure(figsize=(10, 6))
ax = result['Siniestralidad_Mensual'].plot(kind='bar', color='blue')
# Personalizar el gráfico
plt.title('Siniestralidad Mensual')
plt.xlabel('Fecha')
plt.ylabel('Siniestralidad Mensual')
plt.grid(axis='y')

# Mostrar las cantidades sobre las barras
for p in ax.patches:
    ax.annotate(f"{p.get_height():,.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, -10), textcoords='offset points')
plt.savefig('Siniestralidad_Mensual.png')
# Mostrar el gráfico
#plt.show() #Quitar el "#" si se quiere mostrar el gráfico.

#Para usarlo en el PDF
result['Siniestralidad_Mensual'] = result['Siniestralidad_Mensual'].apply(lambda x: f'{x:,.2f}')

''' 
FLUJO CONSULTA 2: Cobertura con mayor y menor cantidad de siniestros

'''

#De la tabla status traemos el tipo de coberturas y lo cruzamos con los diferentes
#siniestros que tienen algún tipo de cobertura en la tabla service.
result_=pd.merge(left=service,right=status,left_on='coverage_id',right_on='id')

#Agrupar por tipo de cobertura y sumar los siniestros.
result_=result_.groupby(['coverage_id', 'name', 'description_y']).size().reset_index(name='Siniestros').sort_values('Siniestros',ascending=False)
result_=result_.reset_index(drop=True)

mayor_cantidad_siniestros=result_[result_['Siniestros'] == result_['Siniestros'].max()]
menor_cantidad_siniestros=result_[result_['Siniestros'] == result_['Siniestros'].min()]
print('\n2.- Cobertura con mayor y menor cantidad de siniestros:')
print('\n-Mayor Cantidad:\n',mayor_cantidad_siniestros)
print('\n-Menor Cantidad:\n',menor_cantidad_siniestros)

print('\n-Tabla General de Siniestros: \n',result_)

'''-----------------------------------GRÁFICOS PARA EL REPORTE PDF----------------------------------'''

# Crear la gráfica de barras horizontales
plt.figure(figsize=(10, 6))
ax=sns.barplot(x='Siniestros', y='name', data=result_, hue='description_y')

# Añadir etiquetas y título
plt.xlabel('Siniestros')
plt.ylabel('Cobertura (Name)')
plt.title('Siniestros por Cobertura')

# Mostrar la leyenda
plt.legend(title='Descripción')
# Añadir números a cada barra

for p in ax.patches:
    ax.annotate(f'{p.get_width()}', (p.get_x() + p.get_width() + 5, p.get_y() + p.get_height() / 2), ha='center', va='center')
#Save
plt.savefig('Siniestros.png')

# Mostrar el gráfico
#plt.show() #Quitar el "#" si se quiere mostrar el gráfico.


''' 

FLUJO CONSULTA 3: Partner con mayor y menor siniestralidad

'''
#Copia para no alterar las tablas para los siguientes cálculos:
service_c1=service.copy()
#Eliminamos nulos
service_c1.dropna(subset=['amount'], inplace=True)
service_c1=service_c1.reset_index(drop=True)
#Unión de Tablas
merged_df = pd.merge(left=claim, right=people, left_on='id', right_on='claim_id')
result_merge=pd.merge(left=service_c1,right=merged_df,left_on='people_id',right_on='id_y')

# Definir patrones, valor comercial del auto y porcentaje de la póliza.
patrones2 = ["Robo Total", "Daños materiales"]
commercial_value2 = 100000
porcentaje_aumento2 = 0.05

# Llamar a la función para buscar y actualizar en 'result_merge'
buscar_y_actualizar(result_merge, status, patrones2, commercial_value2, porcentaje_aumento2)

#Realizando la suma del costo de los siniestros agrupados por el identificador de póliza
#El siniestro tiene un partner asignado hasta su cierre, por lo que se puedo realizar la
#suma de los siniestros directamente.
result2 = result_merge.groupby(result_merge['policy_number'].str.slice(0, 2)).agg({'amount': 'sum'})
result2.sort_values('amount',ascending=False,inplace=True)

menor_sinestrialidad=result2.head(1)
mayor_sinestrialidad=result2.tail(1)

print("\n3.- Partner con mayor y menor siniestralidad:\n")
print(f"\n-Mayor siniestralidad por partner:\n{mayor_sinestrialidad}")
print(f"\n-Menor siniestralidad por partner:\n{menor_sinestrialidad}")

print(f"\n-Siniestralidades por partner:\n{result2}")

'''-----------------------------------GRÁFICOS PARA EL REPORTE PDF----------------------------------'''
# Crear el gráfico de barras
plt.figure(figsize=(10, 6))
ax = result2['amount'].plot(kind='bar', color='blue')

# Personalizar el gráfico
plt.title('Siniestralidad por partner')
plt.xlabel('Partner')
plt.ylabel('Cantidad')
plt.grid(axis='y')

# Mostrar las cantidades sobre las barras
for p in ax.patches:
    ax.annotate(f"{p.get_height():,.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, -10), textcoords='offset points')
plt.savefig('Siniestralidad_Partner.png')
# Mostrar el gráfico
#plt.show() #Quitar el "#" si se quiere mostrar el gráfico.

'''
FLUJO CONSULTA 3.1: Severidad promedio del partner con mayor y menor siniestralidad

'''

#Aquí ya se tiene los gastos de siniestros con la suma del deducible aplicado únicamente en 
# coberturas de daños materiales y robo total.
result_merge_aux=result_merge.copy()

#Eliminamos servicios con monto igual con cero para no afectar el promedio:
result_merge_aux = result_merge_aux[result_merge_aux['amount'] != 0].reset_index(drop=True)

#Nos quedamos con los identificadores de partners
result_merge_aux['policy_number']=result_merge_aux['policy_number'].str.slice(0,2)

#Se obtiene la suma del siniestro agrupado por people_id y su respectiva póliza.
result_policy = result_merge_aux.groupby(['people_id', 'policy_number'])['amount'].sum().reset_index()
result_pattern_avg = result_policy.groupby('policy_number')['amount'].mean().reset_index()
result_pattern_avg.sort_values('amount').reset_index(drop=True)
prom_partner_min=result_pattern_avg[result_pattern_avg['policy_number']== menor_sinestrialidad.index[0]]
prom_partner_max=result_pattern_avg[result_pattern_avg['policy_number']== mayor_sinestrialidad.index[0]]

print("\n3.1- Severidad promedio del partner con mayor y menor siniestralidad:")
print(f"\n-Promedio de severidad del partner con mayor siniestralidad:\n{prom_partner_max}")
print(f"\n-Promedio de severidad del partner con menor siniestralidad:\n{prom_partner_min}")

print(f"\n-Severidad promedio por partner:\n{result_pattern_avg}")


'''-----------------------------------GRÁFICOS PARA EL REPORTE PDF----------------------------------'''

# Crear el gráfico de barras
plt.figure(figsize=(10, 6))
ax = plt.bar(result_pattern_avg['policy_number'], result_pattern_avg['amount'], color='blue')

# Personalizar el gráfico
plt.title('Severidad promedio por partner')
plt.xlabel('Partner')
plt.ylabel('Severidad promedio')
plt.grid(axis='y')

# Función para agregar etiquetas de valores en las barras
def autolabel(bars):
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval,
                 f'{yval:,.2f}',
                 ha='center', va='bottom' if yval > 0 else 'top', color='black')

# Agregar etiquetas de valores en las barras
autolabel(ax)

# Mostrar el gráfico
plt.savefig('Siniestralidad_Promedio_Partner.png')
# Mostrar el gráfico
#plt.show() #Quitar el "#" si se quiere mostrar el gráfico.

#Para usarlo en el PDF
prom_partner_max['amount'] = prom_partner_max['amount'].apply(lambda x: f'{x:,.2f}')
prom_partner_min['amount'] = prom_partner_min['amount'].apply(lambda x: f'{x:,.2f}')

''' 

FLUJO CONSULTA 4: Rango etario con mayor y menor cantidad de usuarios siniestrados

'''

# Crear una copia del DataFrame
people_c2 = people.copy()

# Eliminar filas con valores nulos en la columna 'birthdate'
people_c2 = people_c2.dropna(subset=['birthdate'])

# Eliminar fechas futuras
people_c2 = people_c2[people_c2['birthdate'] <= datetime.now()]

# Calcular la edad y crear la columna 'age'
people_c2['age'] = (datetime.now() - people_c2['birthdate']).apply(lambda x: x.days // 365.25)

# Filtrar personas mayores de 18 y menores de 70 años
people_c2 = people_c2[(people_c2['age'] > 18) & (people_c2['age'] < 70)]

# Definir los rangos etarios
bins = [18, 27, 36, 45, 54, 63, 70]
labels = ['18-26', '27-35', '36-44', '45-53', '54-62', '63-70']

# Asignar usuarios a los rangos etarios
people_c2['age_group'] = pd.cut(people_c2['age'], bins=bins,right=False,labels=labels).copy()

# Agrupar por rango etario y contar usuarios siniestrados
resultados = people_c2.groupby('age_group').size()

# Filtrar los resultados donde la cantidad no es cero
resultados = resultados[resultados != 0]

# Filtrar los resultados donde la cantidad no es cero
resultados = resultados[resultados != 0]
#Esto es para el informe PDF
mayor_cantidad = resultados.idxmax()
menor_cantidad = resultados.idxmin()

print("\n4.- Rango etario con mayor y menor cantidad de usuarios siniestrados:")
print(f"\n-Rango etario con mayor cantidad de usuarios siniestrados:\n{mayor_cantidad}")
print(f"\n-Rango etario con menor cantidad de usuarios siniestrados:\n{menor_cantidad}")

print(f"\n-Siniestros por rangos etarios:\n{resultados}")


'''-----------------------------------GRÁFICOS PARA EL REPORTE PDF----------------------------------'''

# Crear el gráfico de barras
plt.figure(figsize=(10, 6))
ax = resultados.plot(kind='bar', color='blue')

# Personalizar el gráfico
plt.title('Cantidad de Usuarios por Rango Etario')
plt.xlabel('Rango de Edad')
plt.ylabel('Usuarios')
plt.grid(axis='y')

# Mostrar las cantidades sobre las barras
for p in ax.patches:
    ax.annotate(f"{p.get_height():,.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 4), textcoords='offset points')
plt.xticks(rotation=0, ha="right")
plt.savefig('RangoEtario.png')

# Mostrar el gráfico
#plt.show() #Quitar el "#" si se quiere mostrar el gráfico.

''' 

FLUJO CONSULTA 4.1:Severidad promedio del rango etario con mayor y menor cantidad de usuarios siniestrados

'''
#Unión de tablas service y people
merge_range_et_service=pd.merge(left=service,right=people_c2,left_on='people_id',right_on='id')

#Calculo de deducibles para las coberturas que aplique.
patrones2 = ["Robo Total", "Daños materiales"]
commercial_value2 = 100000
porcentaje_aumento2 = 0.05
buscar_y_actualizar(merge_range_et_service, status, patrones2, commercial_value2, porcentaje_aumento2)

#Se eliminan los valores NaN asumiendo que estos son registros que no son gastos.
merge_range_et_service.dropna(subset=['amount'], inplace=True)

#Suma de siniestros por persona con deducibles aplicables.
Sum_niestros=merge_range_et_service.groupby(['people_id'])['amount'].sum().reset_index()

#Unión de la suma de siniestros  con la tabla people para tener el rango etario.
merge_range_et_siniestros=pd.merge(left=Sum_niestros,right=people_c2,left_on='people_id',right_on='id')

#Agrupar por rango etario y obtener el promedio.
Promedio=merge_range_et_siniestros.groupby(['age_group'])['amount'].mean().reset_index()
#De obtenerse valores nulos eliminarlos porque afectan al gráfico y no, nos sirven
Promedio.dropna(inplace=True)
#Convertir a str para poder gráficar.
Promedio['age_group'] = Promedio['age_group'].astype(str)

'''-----------------------------------GRÁFICOS PARA EL REPORTE PDF----------------------------------'''

# Crear el gráfico de barras
plt.figure(figsize=(10, 6))
ax = plt.bar(Promedio['age_group'], Promedio['amount'], color='blue')

# Personalizar el gráfico
plt.title('Severidad promedio por Rango Etario')
plt.xlabel('Rango')
plt.ylabel('Severidad promedio')
plt.grid(axis='y')

# Función para agregar etiquetas de valores en las barras
def autolabel(bars):
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval,
                 f'{yval:,.2f}',
                 ha='center', va='bottom' if yval > 0 else 'top', color='black')

# Agregar etiquetas de valores en las barras
autolabel(ax)

# Mostrar el gráfico
plt.savefig('Severidad_Etario.png')
# Mostrar el gráfico
#plt.show() #Quitar el "#" si se quiere mostrar el gráfico.

#Para  el informe del PDF
#Para el PDF
Promedio['amount'] = Promedio['amount'].apply(lambda x: f'{x:,.2f}')
rango_prom_mayor=Promedio[Promedio['age_group']==mayor_cantidad].reset_index(drop=True)
rango_prom_mayor=f"{rango_prom_mayor['age_group'][0]}: {rango_prom_mayor['amount'][0][0:]}"
rango_prom_menor=Promedio[Promedio['age_group']==menor_cantidad].reset_index()
rango_prom_menor=f"{rango_prom_menor['age_group'][0]}: {rango_prom_menor['amount'][0][0:]}"

#Mostrar resultados en pantalla:

print("\n4.1- Severidad promedio del rango etario con mayor y menor cantidad de usuarios siniestrados:")
print(f"\n-Severidad promedio del rango etario con mayor cantidad de usuarios siniestrados:\n{rango_prom_mayor}")
print(f"\n-Severidad promedio del rango etario con menor cantidad de usuarios siniestrados:\n{rango_prom_menor}")

print(f"\n-Severidad promedio por rangos etarios:\n{Promedio}")

# Llamar a la función para crear el informe PDF
create_pdf(result,mayor_cantidad_siniestros,menor_cantidad_siniestros,mayor_sinestrialidad,prom_partner_max,menor_sinestrialidad,prom_partner_min,mayor_cantidad,menor_cantidad,rango_prom_mayor,rango_prom_menor)

