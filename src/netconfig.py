import pandas as pd
import ipaddress
from openpyxl import load_workbook
import configparser
import os

# Cargar el archivo de configuracion
config = configparser.ConfigParser()
config.read("src/config.ini")

# Leer valores del archivo de configuracion
base_network = ipaddress.IPv4Network(config["netconfig"].get("base_network")) # Rango base
subnet_prefix = config["netconfig"].getint("subnet_prefix") # Tamaño de las subredes (cada razon_social tendrá una subred única)
database_path = config["netconfig"].get("database_path")
output_path = config["output"].get("output_path") + "/db/"

# Asegurarse que la carpeta de salida exista
os.makedirs(output_path, exist_ok=True)

output_excel = os.path.join(output_path, os.path.basename(database_path))
output_csv = os.path.join(output_path, os.path.basename(database_path).replace(".xlsx", ".csv"))

# Funcion para generar nombres de VPN únicos en mayúsculas, reemplazando espacios por barra baja (_)
def generate_vpn_name(punto_de_venta):
    if pd.isna(punto_de_venta) or not punto_de_venta.strip():  # Verificar si el nombre está vacío o es nulo
        return "VPN_DEFAULT"  # Nombre predeterminado si no hay punto_de_venta
    
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
    raise FileNotFoundError(f"No se encontro el archivo {database_path}. Asegúrate de crearlo primero.")

# Lista de subredes ya asignadas por razon_social
subnets_by_client = df.dropna(subset=["razon_social", "subred"]).set_index("razon_social")["subred"].to_dict()

# Generar subredes no usadas
used_subnets = set(subnets_by_client.values())
available_subnets = (str(subnet) for subnet in base_network.subnets(new_prefix=subnet_prefix))
unused_subnets = (subnet for subnet in available_subnets if subnet not in used_subnets)

# Identificar razones_sociales sin subred asignada y asignarles una subred única
for index, row in df.iterrows():
    if pd.notna(row["grupo"]):
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
                raise ValueError("No hay más subredes disponibles para asignar.")
            df.at[index, "subred"] = new_subnet
            subnets_by_client[razon_social] = new_subnet  # Actualizar el registro de subredes asignadas

# Generar IP única dentro de cada subred
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

df["nombre_vpn"] = df.apply(
    lambda row: generate_vpn_name(row["punto_de_venta"]) if pd.notna(row["ip"]) else None,
    axis=1
)


# Cargar el archivo Excel existente con openpyxl para mantener su formato
workbook = load_workbook(database_path)
worksheet = workbook.active

# Escribir datos actualizados en el archivo Excel sin alterar su formato
for index, row in df.iterrows():
    worksheet[f"A{index + 2}"] = row["grupo"]   # Ajusta las columnas según tu archivo
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
