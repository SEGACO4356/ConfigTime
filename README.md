# 🕐 TimeSync Tool

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey)

**Solución profesional para errores de sincronización temporal en pruebas de penetración Active Directory**

## 📖 Descripción

TimeSync Tool es una utilidad especializada en Python diseñada para resolver el error **"Clock Skew Too Great"** en autenticaciones Kerberos durante pruebas de penetración y evaluaciones de seguridad. El script sincroniza automáticamente el tiempo de tu sistema con máquinas objetivo en entornos Active Directory, permitiendo la ejecución exitosa de herramientas Impacket y otras pruebas de seguridad sensibles al tiempo.

## 🚀 Características Principales

| Característica | Descripción |
|---------------|-------------|
| **🔄 Sincronización Automática** | Sincroniza el reloj del sistema con controladores de dominio y máquinas objetivo |
| **💾 Backup & Restauración** | Crea respaldos automáticos de configuración de zona horaria y hora del sistema |
| **🎯 Múltiples Métodos** | Soporta sincronización NTP y configuración manual de hora |
| **🔧 Solucionador de Kerberos** | Enfocado en resolver errores `KRB_AP_ERR_SKEW` en Active Directory |
| **📊 Seguimiento Visual** | Barras de progreso usando librería `pwn` para mejor experiencia de usuario |
| **🛡️ Características de Seguridad** | Deshabilita NTP automáticamente para prevenir reversiones de tiempo |

## 📋 Tabla de Contenidos

- [Instalación](#-instalación)
- [Uso](#-uso)
- [Ejemplos](#-ejemplos)
- [Funciones Principales](#-funciones-principales)
- [Solución de Problemas](#-solución-de-problemas)
- [Dependencias](#-dependencias)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)

## 🛠️ Instalación

### Prerrequisitos del Sistema
```bash
# Instalar ntpdate (requerido para sincronización NTP)
sudo apt update && sudo apt install ntpdate

# En sistemas basados en Red Hat/CentOS:
# sudo yum install ntpdate
```

### Instalación de Dependencias de Python
```bash
# Clonar o descargar el script
git clone <repository-url>
cd timesync-tool

# Instalar dependencias de Python
pip3 install -r requirements.txt
```

### Archivo requirements.txt
```plaintext
ntplib==0.4.0
requests>=2.31.0
pwn>=4.9.0
```

## 🎮 Uso

### Sincronización Básica
```bash
# Sincronizar con máquina objetivo
sudo python3 configTime.py -t 10.10.11.76

# Sincronizar y mostrar diferencias de tiempo
sudo python3 configTime.py -t 192.168.1.100 --verbose
```

### Restauración y Verificación
```bash
# Restaurar configuración original de tiempo
sudo python3 configTime.py --restore

# Verificar estado del backup
sudo python3 configTime.py --check-backup

# Establecer hora manualmente
sudo python3 configTime.py --target-time "2025-01-01 12:00:00"
```

### Modo Avanzado
```bash
# Combinar sincronización con verificación
sudo python3 configTime.py -t 10.10.11.76 --check-backup

# Usar servidores NTP específicos
sudo python3 configTime.py -t dc.corporation.com --ntp-servers "time.google.com,pool.ntp.org"
```

## 📝 Ejemplos

### Ejemplo 1: Resolver Error Kerberos
```bash
# Error típico: KRB_AP_ERR_SKEW(Clock skew too great)
# Solución: Sincronizar con el DC
sudo python3 configTime.py -t dc.voleur.htb

# Luego ejecutar Impacket normalmente
impacket-getTGT voleur.htb/user:Password123
```

### Ejemplo 2: Entorno de Pruebas
```bash
# 1. Verificar backup actual
sudo python3 configTime.py --check-backup

# 2. Sincronizar con objetivo
sudo python3 configTime.py -t 10.10.11.76

# 3. Ejecutar herramientas de pentesting
impacket-secretsdump -k -no-pass VICTIM.DC

# 4. Restaurar configuración original
sudo python3 configTime.py --restore
```

## 🔧 Funciones Principales

### `backup_timezone()`
- Crea respaldo de zona horaria y configuración actual
- Almacena timestamp exacto del momento del backup
- Guarda variable de entorno TZ si existe

### `restore_time()`
- Restaura hora del sistema usando NTP como método principal
- Incluye respaldo manual interactivo
- Maneja ajustes específicos de diferencia de días

### `get_victim_date(target)`
- Obtiene hora exacta de máquina objetivo via NTP
- Soporta múltiples servidores de respaldo
- Timeout configurable para entornos con latencia

### `calculate_and_synchronize()`
- Calcula diferencias temporales precisas
- Sincroniza reloj del sistema automáticamente
- Proporciona feedback detallado del proceso

## 🚨 Solución de Problemas

### Error Común: "Clock Skew Too Great"
```bash
# Síntoma: Kerberos SessionError: KRB_AP_ERR_SKEW
# Solución: 
sudo python3 configTime.py -t <DC_IP>
```

### Error: Comando ntpdate no encontrado
```bash
# Solución: Instalar ntpdate
sudo apt install ntpdate
```

### Error: Permisos insuficientes
```bash
# Solución: Ejecutar como root
sudo python3 configTime.py [opciones]
```

### Problema: Hora se revierte automáticamente
```bash
# El script deshabilita NTP temporalmente para evitar esto
# Si persiste, verificar servicios de tiempo:
sudo systemctl status systemd-timesyncd
```

## 📊 Dependencias

### Python (Requerido)
- **Python 3.6+** - Lenguaje base del script

### Paquetes de Sistema
- **ntpdate** - Cliente NTP para sincronización
- **timedatectl** - Gestor de tiempo del sistema (systemd)

### Librerías Python
| Librería | Función |
|----------|---------|
| **ntplib** | Comunicación con servidores NTP |
| **requests** | Solicitudes HTTP a APIs de tiempo |
| **pwn** | Interfaz de usuario y barras de progreso |
| **datetime** | Manipulación de fechas y horas |
| **subprocess** | Ejecución de comandos del sistema |

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo licencia MIT. Ver `LICENSE` para más información.

## ⚠️ Aviso Legal

Este tool está diseñado **exclusivamente** para:
- Pruebas de penetración autorizadas
- Investigación de seguridad
- Entornos de aprendizaje
- Auditorías de seguridad legítimas

**No utilizar para actividades ilegales.** El uso de esta herramienta es responsabilidad del usuario.

---

**¿Problemas o sugerencias?** Abre un issue en el repositorio del proyecto.

**¿Te ayudó este tool?** ¡Considera darle una ⭐ en GitHub!
