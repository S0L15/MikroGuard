import csv
import configparser
from wireguardconfig import output_csv
from os import makedirs

# Cargar el archivo de configuración
config = configparser.ConfigParser()
config.read("src/config.ini")

# Leer valores del archivo de configuración
input_csv = output_csv
output_path = config["output"].get("output_path") + "/mikrotik/"

# Crear los directorios de salida si no existen
makedirs(output_path, exist_ok=True)

# Leer las subredes desde el archivo CSV
subredes = []
clientes = []
nombresVpn = []
ips = []
clavesPublica = []

# Conjunto para verificar duplicados
subredes_set = set()
clientes_set = set()
nombresVpn_set = set()
ips_set = set()
clavesPublica_set = set()

with open(input_csv, "r") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        subred = row.get("subred")
        cliente = row.get("cliente")
        nombreVpn = row.get("nombre vpn")
        ip = row.get("ip")
        clavePublica = row.get("clave publica")

        if subred and subred not in subredes_set:  # Verifica si la subred ya fue agregada
            subredes.append(subred)
            subredes_set.add(subred)
        if cliente and cliente not in clientes_set:  # Verifica si el cliente ya fue agregado
            clientes.append(cliente)
            clientes_set.add(cliente)
        if nombreVpn and nombreVpn not in nombresVpn_set:  # Verifica si el nombreVpn ya fue agregado
            nombresVpn.append(nombreVpn)
            nombresVpn_set.add(nombreVpn)
        if ip and ip not in ips_set:  # Verifica si la ip ya fue agregada
            ips.append(ip)
            ips_set.add(ip)
        if clavePublica and clavePublica not in clavesPublica_set:  # Verifica si la clave pública ya fue agregada
            clavesPublica.append(clavePublica)
            clavesPublica_set.add(clavePublica)

# Convertir las listas a cadenas separadas por espacios, con comillas y punto y coma al final de cada elemento
subredes_str = "".join([f'"{subred}";\n' for subred in subredes])
clientes_str = "".join([f'"{cliente}";\n' for cliente in clientes])
nombresVpn_str = "".join([f'"{nombreVpn}";\n' for nombreVpn in nombresVpn])
ips_str = "".join([f'"{ip}";\n' for ip in ips])
clavesPublica_str = "".join([f'"{clavePublica}";\n' for clavePublica in clavesPublica])

# Generar el script para MikroTik - Subredes
script_lines_address = [
    "# Script generado para agregar subredes a MikroTik",
    ":local subredes {\n" + subredes_str[:-2] + "\n}\n",  # Lista de subredes con elementos separados por espacios y punto y coma
    ":local clientes {\n" + clientes_str[:-2] + "\n}"   # Lista de clientes con elementos separados por espacios y punto y coma
]

script_lines_address.append(""" 
# Verificar si cada subred ya esta configurada y agregarla si es necesario
:for i from=0 to=([ :len $subredes ] - 1) do={
    :local subred [:pick $subredes $i]
    :local cliente [:pick $clientes $i]

    # Verificar si la subred ya esta en la lista de direcciones
    :local encontrado false
    :foreach direccion in=[/ip address find] do={
        :if ( [/ip address get $direccion address] = $subred ) do={
            :set encontrado true
        }
    }

    # Si la subred no esta en la lista, agregarla
    :if ($encontrado = false) do={
        /ip address add address=$subred interface=WGTEST comment="WG $cliente"
        :log info ("Subred agregada: " . $subred . " con comentario: " . $cliente)
    } else={
        :log info ("La subred ya existe: " . $subred)
    }
}
""")

# Generar el script para MikroTik - Peers
script_lines_peers = [
    "# Script generado para agregar peers a MikroTik",
    ":local nombresVpn {\n" + nombresVpn_str[:-2] + "\n}\n",  # Lista de nombres vpn con elementos separados por espacios y punto y coma
    ":local ips {\n" + ips_str[:-2] + "\n}\n",   # Lista de ips con elementos separados por espacios y punto y coma
    ":local clavesPublica {\n" + clavesPublica_str[:-2] + "\n}"  # Lista de claves publicas con elementos separados por espacios y punto y coma
]

script_lines_peers.append(""" 
# Verificar si cada peer ya esta configurado y agregarlo si es necesario
:for i from=0 to=([ :len $nombresVpn ] - 1) do={
    :local nombreVpn [:pick $nombresVpn $i]
    :local ipList [:pick $ips $i]
    :local clavePublica [:pick $clavesPublica $i]

    # Verificar si el peer ya esta en la lista de direcciones
    :local encontrado false
    :foreach direccion in=[/interface wireguard peers find] do={  # Verificación de peers de WireGuard
        :if ( [/interface wireguard peers get $direccion allowed-address] = $ipList ) do={
            :set encontrado true
        }
    }

    # Si el peer no esta en la lista, agregarlo
    :if ($encontrado = false) do={
        /interface wireguard peers add name=$nombreVpn public-key=$clavePublica allowed-address=$ipList endpoint-address="179.50.75.210" endpoint-port=13231 interface=WG persistent-keepalive=30
        :log info ("Peer agregado: " . $nombreVpn . " con ip: " . $ipList)
    } else={
        :log info ("El peer ya existe: " . $nombreVpn)
    }
}
""")

# Guardar el script generado en un archivo .rsc
with open(output_path + "mikrotik_address.rsc", "w") as outfile:
    outfile.write("\n".join(script_lines_address))

# Guardar el script generado en un archivo .rsc
with open(output_path + "mikrotik_peers.rsc", "w") as outfile:
    outfile.write("\n".join(script_lines_peers))

print(f"Script de MikroTik generado: {output_path + "mikrotik_address.rsc"}")
print(f"Script de MikroTik generado: {output_path + "mikrotik_peers.rsc"}")
