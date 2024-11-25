# Proyecto de Automatización de Configuración de Redes

Este proyecto automatiza tareas relacionadas con la asignación de subredes, la configuración de túneles WireGuard y la generación de scripts para MikroTik. 

## Archivos y Funcionalidades

### 1. **netconfig.py**
Este script gestiona la configuración inicial de la base de datos de clientes, subredes y grupos en un archivo Excel. Además, genera un archivo CSV con los datos procesados.

#### Funcionalidades principales:
- **Asignación de subredes:** Genera subredes únicas para clientes que no tienen una asignada, respetando un tamaño definido.
- **Agrupación de clientes:** Organiza clientes en grupos de tamaño definido.
- **Generación de IPs:** Asigna direcciones IP únicas dentro de las subredes asignadas.
- **Creación de nombres de VPN:** Estandariza nombres de VPN en mayúsculas, reemplazando espacios por guiones bajos.
- **Actualización de archivos:** Modifica un archivo Excel existente manteniendo su formato y genera un archivo CSV.

#### Entrada:
- Archivo Excel con los datos iniciales (por defecto `db/test.xlsx`).

#### Salida:
- Archivo Excel actualizado.
- Archivo CSV con los datos procesados.

---

### 2. **wireguardconfig.py**
Este script genera configuraciones de túneles para clientes en WireGuard y scripts para MikroTik.

#### Funcionalidades principales:
- **Generación de claves:** Crea claves privadas y públicas para clientes si no existen.
- **Creación de archivos `.conf`:** Genera archivos de configuración para cada cliente en el directorio `output/tuneles`.
- **Actualización de base de datos:** Agrega claves públicas y privadas al archivo Excel y CSV.
- **Generación de scripts para MikroTik:** Produce scripts para configurar peers y subredes en routers MikroTik.

#### Entrada:
- Archivo Excel con datos de clientes (`db/test.xlsx`).

#### Salida:
- Configuraciones WireGuard en `output/tuneles`.
- Scripts MikroTik en `output/mikrotik`:
  - `mikrotik_wireguard_peers.rsc`: Configura los peers.
  - `mikrotik_subnets.rsc`: Configura las subredes.
- Archivos CSV y Excel actualizados.

---

### 3. **mikrotikconfig.py**
Este script genera scripts detallados para configurar subredes e interfaces de peers en MikroTik utilizando los datos procesados en el archivo CSV.

#### Funcionalidades principales:
- **Lectura de datos:** Obtiene información de subredes, clientes, nombres de VPN, direcciones IP y claves públicas desde un archivo CSV.
- **Generación de scripts MikroTik:** Produce scripts para agregar subredes y peers de WireGuard en formato `.rsc`.
- **Verificación de duplicados:** Asegura que no se dupliquen subredes ni peers en los scripts generados.

#### Entrada:
- Archivo CSV generado por `netconfig.py` o `wireguardconfig.py` (por defecto `db/test.csv`).

#### Salida:
- `mikrotik_address.rsc`: Script para configurar subredes.
- `mikrotik_peers.rsc`: Script para configurar peers de WireGuard.

---

## Requisitos Previos

- **Librerías de Python:**  
  Asegúrate de instalar las siguientes librerías:
  ```bash
  pip install pandas openpyxl
