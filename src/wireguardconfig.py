import os
import subprocess
import pandas as pd
from openpyxl import load_workbook
import csv
import configparser

# Cargar el archivo de configuración
config = configparser.ConfigParser()
config.read("src/config.ini")

# Leer valores del archivo de configuración
database_path = config["netconfig"].get("database_path")
output_path = config["output"].get("output_path")
output_peers_directory = output_path + "/tunnels/" # Directorio para los archivos de los peers WireGuard
public_key_custom_text = config["wireguard"].get("public_key_custom_text")
endpoint_custom_text = config["wireguard"].get("endpoint_custom_text")
port_custom_text = config["wireguard"].get("port_custom_text")

# Archivos de salida
output_csv = os.path.splitext(database_path)[0] + ".csv" # Directorio para el archivo CSV

# Crear los directorios de salida si no existen
os.makedirs(output_peers_directory, exist_ok=True)

# Función para generar claves privadas y públicas
def generate_keys():
    private_key = subprocess.check_output("wg genkey", shell=True).decode("utf-8").strip()
    public_key = subprocess.check_output(f"echo {private_key} | wg pubkey", shell=True).decode("utf-8").strip()
    return private_key, public_key

# Función para leer un archivo .config
def read_peer_config(file_path):
    """Lee un archivo de configuración de WireGuard y devuelve sus parámetros clave."""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "r") as file:
        lines = file.readlines()

    config_data = {}
    for line in lines:
        if line.strip().startswith("PrivateKey"):
            config_data["PrivateKey"] = line.split("=")[-1].strip()
        elif line.strip().startswith("PublicKey"):
            config_data["PublicKey"] = line.split("=")[-1].strip()
        elif line.strip().startswith("Address"):
            config_data["Address"] = line.split("=")[-1].strip()
        elif line.strip().startswith("AllowedIPs"):
            config_data["AllowedIPs"] = line.split("=")[-1].strip()
        elif line.strip().startswith("Endpoint"):
            config_data["Endpoint"] = line.split("=")[-1].strip()

    return config_data

# Cargar datos del archivo Excel
df = pd.read_excel(database_path)

# Leer configuraciones existentes
existing_configs = {}
for index, row in df.iterrows():
    nombre_vpn = row["nombre vpn"]
    if pd.notna(nombre_vpn):
        config_file = os.path.join(output_peers_directory, f"{nombre_vpn}.conf")
        if os.path.exists(config_file):
            existing_configs[nombre_vpn] = read_peer_config(config_file)

# Generar claves y configuraciones
for index, row in df.iterrows():
    nombre_vpn = row["nombre vpn"]
    subred = row["subred"]
    ip = row["ip"]

    # Generar claves privadas y públicas si no existen
    if pd.isna(row["clave publica"]):
        if nombre_vpn in existing_configs:
            # Recuperar claves existentes
            private_key = existing_configs[nombre_vpn]["PrivateKey"]
            public_key = existing_configs[nombre_vpn]["PublicKey"]
        else:
            # Generar nuevas claves
            private_key, public_key = generate_keys()

        # Actualizar la clave pública y privada en el DataFrame
        df.at[index, "clave publica"] = public_key
        df.at[index, "clave privada"] = private_key
    else:
        # Recuperar claves existentes (si no se generaron nuevas)
        if nombre_vpn in existing_configs:
            private_key = existing_configs[nombre_vpn]["PrivateKey"]
        else:
            private_key = "NO_PRIVATE_KEY"  # Placeholder para evitar errores
        public_key = row["clave publica"]

    # Revisar si ya existe un archivo de configuración para el peer
    config_file = os.path.join(output_peers_directory, f"{nombre_vpn}.conf")
    if not os.path.exists(config_file):
        # Si no existe, crear el archivo .config
        peer_config = f"""[Interface]
PrivateKey = {private_key}
Address = {ip}
DNS = 1.1.1.1

[Peer]
PublicKey = {public_key_custom_text}
AllowedIPs = {subred}
Endpoint = {endpoint_custom_text + ":" + port_custom_text}
PersistentKeepalive = 30
"""
        with open(config_file, "w") as outfile:
            outfile.write(peer_config)

# Reordenar columnas y agregar clave privada como última columna
df = df[["grupo", "subred", "cliente", "punto de venta", "nombre vpn", "ip", "clave publica", "clave privada"]]

# Guardar el DataFrame actualizado en el archivo CSV
df.to_csv(output_csv, index=False)

# Actualizar el archivo Excel sin modificar el formato
workbook = load_workbook(database_path)
worksheet = workbook.active

# Escribir los valores en el orden correcto
header_map = {  # Mapeo de columnas para Excel
    "grupo": "A",
    "subred": "B",
    "cliente": "C",
    "punto de venta": "D",
    "nombre vpn": "E",
    "ip": "F",
    "clave publica": "G",
    "clave privada": "H",  # Columna para la clave privada
}

# Escribir encabezados
for col_name, col_letter in header_map.items():
    worksheet[f"{col_letter}1"] = col_name

# Escribir datos
for index, row in df.iterrows():
    for col_name, col_letter in header_map.items():
        worksheet[f"{col_letter}{index + 2}"] = row[col_name]

workbook.save(database_path)

print(f"Archivos generados y actualizados:\n- Configuraciones de peers en: {output_peers_directory}\n- CSV: {output_csv}\n- Excel: {database_path}")