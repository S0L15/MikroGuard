import pandas as pd
import ipaddress
from openpyxl import load_workbook
import configparser
import os

# Cargar el archivo de configuración
config = configparser.ConfigParser()
config.read("src/config.ini")

# Leer valores del archivo de configuración
base_network = ipaddress.IPv4Network(config["netconfig"].get("base_network")) # Rango base
subnet_prefix = config["netconfig"].getint("subnet_prefix") # Tamaño de las subredes (cada cliente tendrá una subred única)
clientes_por_grupo = config["netconfig"].getint("clientes_por_grupo") # Número máximo de clientes por grupo
database_path = config["netconfig"].get("database_path")
output_path = config["output"].get("output_path") + "/db/"

# Asegurarse que la carpeta de salida exista
os.makedirs(output_path, exist_ok=True)

output_excel = os.path.join(output_path, os.path.basename(database_path))
output_csv = os.path.join(output_path, os.path.basename(database_path).replace(".xlsx", ".csv"))

# Función para generar nombres de VPN únicos en mayúsculas, reemplazando espacios por barra baja (_)
def generate_vpn_name(punto_de_venta):
    if pd.isna(punto_de_venta) or not punto_de_venta.strip():  # Verificar si el nombre está vacío o es nulo
        return "VPN_DEFAULT"  # Nombre predeterminado si no hay punto de venta
    
    # Reemplazar espacios por barra baja (_) y mantener solo letras, números y guiones bajos
    vpn_name = punto_de_venta.strip()  # Eliminar espacios al inicio y al final
    vpn_name = vpn_name.replace(" ", "_")  # Reemplazar espacios por barra baja

    # Mantener solo caracteres alfanuméricos y guiones bajos, eliminando otros caracteres no válidos
    vpn_name = ''.join(e for e in vpn_name if e.isalnum() or e == '_')
    
    # Convertir todo a mayúsculas para estandarizar
    vpn_name = vpn_name.upper()
    
    return vpn_name

# Leer datos del archivo Excel existente
try:
    df = pd.read_excel(database_path)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el archivo {database_path}. Asegúrate de crearlo primero.")

# Lista de subredes ya asignadas por cliente
subnets_by_client = df.dropna(subset=["cliente", "subred"]).set_index("cliente")["subred"].to_dict()

# Generar subredes no usadas
used_subnets = set(subnets_by_client.values())
available_subnets = (str(subnet) for subnet in base_network.subnets(new_prefix=subnet_prefix))
unused_subnets = (subnet for subnet in available_subnets if subnet not in used_subnets)

# Identificar clientes sin subred asignada y asignarles una subred única
for index, row in df.iterrows():
    cliente = row["cliente"]
    
    if pd.isna(row["subred"]):  # Si no tiene subred asignada
        if cliente in subnets_by_client:  # Si el cliente ya tiene una subred conocida
            df.at[index, "subred"] = subnets_by_client[cliente]
        else:  # Asignar nueva subred
            try:
                new_subnet = next(unused_subnets)
            except StopIteration:
                raise ValueError("No hay más subredes disponibles para asignar.")
            df.at[index, "subred"] = new_subnet
            subnets_by_client[cliente] = new_subnet  # Actualizar el registro de subredes asignadas

# Actualizar los grupos
df["grupo"] = None
group_number = 1
client_count = 0

for index, row in df.iterrows():
    if pd.isna(row["grupo"]):  # Solo actualizar si no tiene grupo asignado
        df.at[index, "grupo"] = group_number
        client_count += 1
        if client_count >= clientes_por_grupo:
            group_number += 1
            client_count = 0

# Generar IP única dentro de cada subred
used_ips = set(df["ip"].dropna())

for index, row in df.iterrows():
    subred = row["subred"]
    if pd.isna(row["ip"]):
        red = ipaddress.IPv4Network(subred, strict=False)
        for ip in red.hosts():
            if str(ip) not in used_ips:
                used_ips.add(str(ip))
                df.at[index, "ip"] = str(ip)
                break

# Generar o actualizar nombres de VPN únicos para cada punto de venta en mayúsculas
df["nombre vpn"] = df["punto de venta"].apply(lambda x: generate_vpn_name(x) if pd.isna(x) or not x.strip() else generate_vpn_name(x))

# Cargar el archivo Excel existente con openpyxl para mantener su formato
workbook = load_workbook(database_path)
worksheet = workbook.active

# Escribir datos actualizados en el archivo Excel sin alterar su formato
for index, row in df.iterrows():
    worksheet[f"A{index + 2}"] = row["grupo"]   # Ajusta las columnas según tu archivo
    worksheet[f"B{index + 2}"] = row["subred"]
    worksheet[f"C{index + 2}"] = row["cliente"]
    worksheet[f"D{index + 2}"] = row["punto de venta"]
    worksheet[f"E{index + 2}"] = row["nombre vpn"]
    worksheet[f"F{index + 2}"] = row["ip"]

# Guardar el archivo Excel actualizado en la ruta de salida
workbook.save(output_excel)

# Guardar un archivo CSV basado en el DataFrame en la ruta de salida
df.to_csv(output_csv, index=False)

print(f"Archivos actualizados guardados en:\n- {output_excel}\n- {output_csv}")
