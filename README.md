# MikroGuard

MikroGuard is a powerful tool designed to assist network administrators in setting up and managing multiple WireGuard peers across different subnets. With its user-friendly interface and automated script generation, MikroGuard streamlines the process of network management, saving time and reducing complexity.

---

## Features

- **Automated WireGuard Peer Creation:** Simplify the configuration and deployment of multiple peers with ease.
- **Customizable Network Settings:** Define subnet structures, network prefixes, and other parameters flexibly.
- **Integration with Existing Databases:** Supports importing client data from predefined databases for seamless setup.
- **Script Automation:** Automatically generate scripts for MikroTik routers and other configurations.
- **Portable Execution:** No installation required—just run the executable.

---

## Installation

1. **Download the Executable:**
   - Visit the [Releases](https://github.com/S0L15/MikroGuard/releases) page on GitHub to download the latest version of MikroGuard.

2. **Run as a Portable Application:**
   - No installation process is needed. Simply double-click the `.exe` file to launch the program.

---

## Usage

1. **Launch the Application:**
   - Run the downloaded `.exe` file.

2. **Set Up Your Configuration:**
   - In the **NetConfig** tab:
     - Define the base network (e.g., `192.168.1.0/24`).
     - Set the network prefix (e.g., `/27`).
     - Specify the number of clients per group (e.g., `4`).
     - Provide the path to the initial database containing the required columns: 
       `["grupo", "subred", "cliente", "punto de venta", "nombre vpn", "ip", "clave publica", "clave privada"]`.

   - In the **WireGuard** tab:
     - Add the public key of the MikroTik router.
     - Specify the endpoint and port for the router.

   - In the **Output Path** section:
     - Select the folder where the result files and scripts will be saved.

3. **Save and Generate Scripts:**
   - Click **Save Config** to store your settings.
   - Click **Run Scripts** to generate configuration files and deployment scripts.

4. **Deploy Configurations:**
   - Use the generated scripts to deploy settings on your network devices.

---

## System Requirements

- **Operating System:** Windows 10 or higher.
- **Python (Development Version Only):** Python 3.12 or higher.

---

## Example Workflow

1. Configure a base network, such as `192.168.1.0/24`.
2. Set up `/27` as the network prefix.
3. Assign `4` clients per group.
4. Import the client data from an initial database (CSV or similar).
5. Add the MikroTik router's public key, endpoint, and port.
6. Save configuration before running the scripts using the **Save Config** button.
6. Generate and deploy the scripts using the **Run Scripts** feature.

---

## Troubleshooting

- **Cannot Run the Executable:**
  - Ensure you have sufficient permissions to execute `.exe` files on your system.
  - Check your antivirus software—some may incorrectly flag the program.

- **Configuration Errors:**
  - Double-check the settings entered in the **NetConfig** and **WireGuard** sections.
  - Verify the format and data integrity of the initial database file.

For additional support, contact the author or refer to the documentation.

---

## Author

**S0L15**

- Email: [d3v.s0l15@gmail.com](mailto:d3v.s0l15@gmail.com)
- GitHub: [S0L15](https://github.com/S0L15)

---

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/). You are free to modify and distribute it as per the license terms.

---

## Contributing

Contributions are welcome! If you have ideas for improvements or new features, feel free to:
- Open an issue on GitHub.
- Submit a pull request with your proposed changes.

---

## Future Plans

- **Multi-language Support:** Expand usability with localization for multiple languages.
- **Advanced Analytics:** Include monitoring and reporting tools for network performance.
- **Cross-Platform Support:** Extend compatibility to Linux and macOS platforms.

---

## Acknowledgments

A big thanks to the open-source community for their support and contributions, which made MikroGuard possible. Special gratitude to users providing feedback for continuous improvement.