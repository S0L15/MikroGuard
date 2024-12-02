import pandas as pd
import ipaddress
from openpyxl import load_workbook
import configparser
import os

# Cargar el archivo de configuracion
config = configparser.ConfigParser()
config.read("src/config.ini")

# Leer valores del archivo de configuracion
base_network = ipaddress.IPv4Network(config["netconfig"].get("base_network"))  # Rango base
subnet_prefix = config["netconfig"].getint("subnet_prefix")  # Tamaño de las subredes
database_path = config["netconfig"].get("database_path")
group_size = config["netconfig"].getint("default_group_size")  # Asegurarse que sea un entero
output_path = config["output"].get("output_path") + "/db/"

# Asegurarse de que la carpeta de salida exista
os.makedirs(output_path, exist_ok=True)

output_excel = os.path.join(output_path, os.path.basename(database_path))
output_csv = os.path.join(output_path, os.path.basename(database_path).replace(".xlsx", ".csv"))

# Funcion para generar nombres de VPN unicos en mayusculas, reemplazando espacios por barra baja (_)
def generate_vpn_name(punto_de_venta):
    if pd.isna(punto_de_venta) or not punto_de_venta.strip():  # Verificar si el nombre esta vacio o es nulo
        return "VPN_DEFAULT"  # Nombre predeterminado si no hay punto_de_venta
    
    # Reemplazar espacios por barra baja (_) y mantener solo letras, numeros y guiones bajos
    vpn_name = punto_de_venta.strip()  # Eliminar espacios al inicio y al final
    vpn_name = vpn_name.replace(" ", "_")  # Reemplazar espacios por barra baja

    # Mantener solo caracteres alfanumericos y guiones bajos, eliminando otros caracteres no validos
    vpn_name = ''.join(e for e in vpn_name if e.isalnum() or e == '_')
    
    # Convertir todo a mayusculas para estandarizar
    vpn_name = vpn_name.upper()
    
    return vpn_name

# Leer datos del archivo Excel existente
try:
    df = pd.read_excel(database_path)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontro el archivo {database_path}. Asegurate de crearlo primero.")

# Asignar grupos predeterminados si no estan definidos
group_counter = 1  # Contador para los grupos predeterminados
assigned_group = {}  # Diccionario para rastrear grupos asignados
device_count = 0  # Contador de dispositivos en el grupo actual

for index, row in df.iterrows():
    if pd.isna(row.get("grupo")):  # Si no tiene grupo asignado
        if device_count >= group_size:  # Si el grupo alcanza el tamaño maximo
            group_counter += 1  # Incrementar el contador de grupos
            device_count = 0  # Reiniciar el contador de dispositivos
        new_group = f"GROUP{group_counter}"
        df.at[index, "grupo"] = new_group
        device_count += 1
    else:
        assigned_group[row["grupo"]] = assigned_group.get(row["grupo"], 0) + 1

# Lista de subredes ya asignadas por razon_social
subnets_by_client = df.dropna(subset=["razon_social", "subred"]).set_index("razon_social")["subred"].to_dict()

# Generar subredes no usadas
used_subnets = set(subnets_by_client.values())
available_subnets = (str(subnet) for subnet in base_network.subnets(new_prefix=subnet_prefix))
unused_subnets = (subnet for subnet in available_subnets if subnet not in used_subnets)

# Identificar razones_sociales sin subred asignada y asignarles una subred unica
for index, row in df.iterrows():
    if pd.notna(row["grupo"]) and row["grupo"][:5] != "GROUP":
        razon_social = row["grupo"]
    elif pd.notna(row["razon_social"]):
        razon_social = row["razon_social"]
    else:
        continue
    
    if pd.isna(row["subred"]):  # Si no tiene subred asignada
        if razon_social in subnets_by_client:  # Si el razon_social ya tiene una subred conocida
            df.at[index, "subred"] = subnets_by_client[razon_social]
        else:  # Asignar nueva subred
            try:
                new_subnet = next(unused_subnets)
            except StopIteration:
                raise ValueError("No hay mas subredes disponibles para asignar.")
            df.at[index, "subred"] = new_subnet
            subnets_by_client[razon_social] = new_subnet  # Actualizar el registro de subredes asignadas

# Generar IP unica dentro de cada subred
used_ips = set(df["ip"].dropna())

for index, row in df.iterrows():
    subred = row["subred"]
    if pd.isna(row["ip"]) and pd.notna(row["subred"]):
        red = ipaddress.IPv4Network(subred, strict=False)
        for ip in red.hosts():
            if str(ip) not in used_ips:
                used_ips.add(str(ip))
                df.at[index, "ip"] = str(ip)
                break

# Generar nombres de VPN
df["nombre_vpn"] = df.apply(
    lambda row: generate_vpn_name(row["punto_de_venta"]) if pd.notna(row["ip"]) else None,
    axis=1
)

# Cargar el archivo Excel existente con openpyxl para mantener su formato
workbook = load_workbook(database_path)
worksheet = workbook.active

# Escribir datos actualizados en el archivo Excel sin alterar su formato
for index, row in df.iterrows():
    worksheet[f"A{index + 2}"] = row["grupo"] # Ajusta las columnas segun tu archivo
    worksheet[f"B{index + 2}"] = row["subred"]
    worksheet[f"C{index + 2}"] = row["razon_social"]
    worksheet[f"D{index + 2}"] = row["punto_de_venta"]
    worksheet[f"E{index + 2}"] = row["nombre_vpn"]
    worksheet[f"F{index + 2}"] = row["ip"]

# Guardar el archivo Excel actualizado en la ruta de salida
workbook.save(output_excel)

# Guardar un archivo CSV basado en el DataFrame en la ruta de salida
df.to_csv(output_csv, index=False)

print(f"Archivos actualizados guardados en:\n- {output_excel}\n- {output_csv}")
