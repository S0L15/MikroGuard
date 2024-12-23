import tkinter as tk
from tkinter import filedialog, messagebox
import configparser
import os
import subprocess
import sys

# Funcion para obtener la ruta correcta al archivo dentro del ejecutable
def get_file_path(filename):
    """Returns file path depending on if the program is running from the .exe or from the source script."""
    if getattr(sys, 'frozen', False):  # Si esta corriendo como un ejecutable de PyInstaller
        # Si es un ejecutable, busca el archivo dentro de la carpeta temporal de PyInstaller
        base_path = sys._MEIPASS
    else:
        # Si esta corriendo como un script, busca los archivos en el directorio actual
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, filename)


# Funciones para manejar configuracion y ejecucion
def load_config():
    """Loads config from config.ini. Sets default values if they don't exist."""
    config = configparser.ConfigParser()
    config_path = get_file_path("config.ini")  # Usar get_file_path para obtener la ruta correcta

    if not os.path.exists(config_path):
        # Crear valores predeterminados si no existe
        config["metadata"] = {
            "project_name = MikroGuard",
            "version = 1.0.0",
            "author = S0L15",
            "email = d3v.s0l15@gmail.com",
            "icon_path = icon\MikroGuard_logo_1.png"
        }
        config["netconfig"] = {
            "base_network": "192.168.1.0",
            "subnet_prefix": "24",
            "database_path": "db/default.xlsx",
            "default_group_size": "4",
            "interface": "WG"
        }
        config["wireguard"] = {
            "public_key_custom_text": "default_public_key",
            "endpoint_custom_text": "127.0.0.1:51820",
            "port_custom_text": "51820",
        }
        config["output"] = {
            "output_path": "src/output/",
        }
        save_config(config)  # Guardar valores predeterminados
    else:
        config.read(config_path)
        # Asegurar claves por defecto si faltan
        config.setdefault("netconfig", {})
        config.setdefault("wireguard", {})
        config.setdefault("output", {})
        config["netconfig"].setdefault("base_network", "192.168.1.0")
        config["netconfig"].setdefault("subnet_prefix", "24")
        config["netconfig"].setdefault("database_path", "db/default.xlsx")
        config["netconfig"].setdefault("default_group_size", "4")
        config["netconfig"].setdefault("interface", "WG")
        config["wireguard"].setdefault("public_key_custom_text", "default_public_key")
        config["wireguard"].setdefault("endpoint_custom_text", "127.0.0.1:51820")
        config["wireguard"].setdefault("port_custom_text", "51820")
        config["output"].setdefault("output_path", "output/")
        config["metadata"].setdefault("project_name", "MikroGuard")
        config["metadata"].setdefault("version", "1.0.0")
        config["metadata"].setdefault("author", "S0L15")
        config["metadata"].setdefault("contact_email", "d3v.s0l15@gmail.com")
        config["metadata"].setdefault("icon_path", "icon\MikroGuard_logo_1.png")
    return config


def save_config(config):
    """Saves config on config.ini"""
    config_path = get_file_path("config.ini")
    with open(config_path, "w") as configfile:
        config.write(configfile)


def run_scripts_in_order(scripts):
    """Runs a list of scripts. If one fails it stops"""
    for script in scripts:
        try:
            subprocess.run(["python", script], check=True)
            messagebox.showinfo("Success", f"{script} executed successfully.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {script} could not be found.")
            return False
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"There was an error running {script}.\n{e}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error runnning {script}.\n{e}")
            return False
    return True

# GUI principal
def main():
    config = load_config()
    icon_path = config["metadata"]["icon_path"]

    root = tk.Tk()
    icon = tk.PhotoImage(file=icon_path)
    root.iconphoto(False, icon)
    root.title(config["metadata"]["project_name"] + " version: " + config["metadata"]["version"])
    root.geometry("550x650")

    # Seccion de NetConfig
    tk.Label(root, text="NetConfig", font=("Arial", 12, "bold")).grid(
        row=0, column=0, columnspan=3, pady=(10, 5)
    )
    # Base Network
    tk.Label(root, text="Base Network:").grid(row=1, column=0, sticky="e", padx=10)
    base_network = tk.Entry(root, width=40)
    base_network.grid(row=1, column=1, pady=5)
    base_network.insert(0, config["netconfig"].get("base_network", "192.168.1.0"))
    # Subnet Prefix
    tk.Label(root, text="Subnet Prefix:").grid(row=2, column=0, sticky="e", padx=10)
    subnet_prefix = tk.Entry(root, width=40)
    subnet_prefix.grid(row=2, column=1, pady=5)
    subnet_prefix.insert(0, config["netconfig"].get("subnet_prefix", "24"))
    # Group Size
    tk.Label(root, text="Group Size:").grid(row=3, column=0, sticky="e", padx=10)
    group_size = tk.Entry(root, width=40)
    group_size.grid(row=3, column=1, pady=5)
    group_size.insert(0, config["netconfig"].get("default_group_size", "4"))
    # Interface
    tk.Label(root, text="MikroTik Interface:").grid(row=4, column=0, sticky="e", padx=10)
    interface = tk.Entry(root, width=40)
    interface.grid(row=4, column=1, pady=5)
    interface.insert(0, config["netconfig"].get("interface", ""))
    # Database Route
    tk.Label(root, text="Database Path:").grid(row=5, column=0, sticky="e", padx=10)
    database_entry = tk.Entry(root, width=40)
    database_entry.grid(row=5, column=1, pady=5)
    database_entry.insert(0, config["netconfig"].get("database_path", ""))

    def select_database_path():
        database = filedialog.askopenfilename(title="Choose File")
        if database:
            database_entry.delete(0, tk.END)
            database_entry.insert(0, database)

    tk.Button(
        root, text="Explore", command=select_database_path, width=10
    ).grid(row=5, column=2, padx=5, pady=5)

    # Seccion de WireGuard
    tk.Label(root, text="WireGuard", font=("Arial", 12, "bold")).grid(
        row=6, column=0, columnspan=3, pady=(20, 5)
    )
    tk.Label(root, text="Router's Public Key:").grid(row=7, column=0, sticky="e", padx=10)
    public_key = tk.Entry(root, width=40)
    public_key.grid(row=7, column=1, pady=5)
    public_key.insert(
        0, config["wireguard"].get("public_key_custom_text", "default_public_key")
    )
    tk.Label(root, text="Endpoint:").grid(row=8, column=0, sticky="e", padx=10)
    endpoint = tk.Entry(root, width=40)
    endpoint.grid(row=8, column=1, pady=5)
    endpoint.insert(0, config["wireguard"].get("endpoint_custom_text", "127.0.0.1"))
    tk.Label(root, text="Port:").grid(row=9, column=0, sticky="e", padx=10)
    port = tk.Entry(root, width=40)
    port.grid(row=9, column=1, pady=5)
    port.insert(0, config["wireguard"].get("port_custom_text", "51820"))

    # Output Path
    tk.Label(root, text="Output Path", font=("Arial", 12, "bold")).grid(row=10, column=0, columnspan=3, pady=(20, 5))
    tk.Label(root, text="Output path for files:").grid(row=11, column=0, sticky="e", padx=10)

    def select_output_path():
        output_path = filedialog.askdirectory(title="Select Folder")
        if output_path:
            output_path_entry.delete(0, tk.END)
            output_path_entry.insert(0, output_path)

    output_path_entry = tk.Entry(root, width=40)
    output_path_entry.grid(row=11, column=1, pady=5)
    output_path_entry.insert(0, config["output"].get("output_path", "output/"))

    tk.Button(
        root, text="Explore", command=select_output_path, width=10
    ).grid(row=11, column=2, padx=5, pady=5)

    def save_config_from_entries():
        """Saves config set by user on config.ini"""
        try:
            config["netconfig"]["base_network"] = base_network.get()
            config["netconfig"]["subnet_prefix"] = subnet_prefix.get()
            config["netconfig"]["database_path"] = database_entry.get()
            config["wireguard"]["public_key_custom_text"] = public_key.get()
            config["wireguard"]["endpoint_custom_text"] = endpoint.get()
            config["wireguard"]["port_custom_text"] = port.get()
            config["output"]["output_path"] = output_path_entry.get()
            save_config(config)
            messagebox.showinfo("Configuracion", "Config saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Config could not be saved: {e}")

    # Boton para guardar la configuracion
    save_button = tk.Button(
        root, text="Save Config", command=save_config_from_entries, width=20
    )
    save_button.grid(row=12, column=0, columnspan=3, pady=(20, 10))

    # Boton para ejecutar scripts
    def run_scripts():
        scripts = [
            get_file_path("netconfig.py"),
            get_file_path("wireguardconfig.py"),
            get_file_path("mikrotikconfig.py")
        ]
        if run_scripts_in_order(scripts):
            messagebox.showinfo("Success", "Scripts executed successfully.")
        else:
            messagebox.showerror("Error", "There was an error while running the scripts")

    run_button = tk.Button(
        root, text="Run Scripts", command=run_scripts, width=20
    )
    run_button.grid(row=13, column=0, columnspan=3, pady=(10, 20))

    root.mainloop()

if __name__ == "__main__":
    main()
