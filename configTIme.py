#!/usr/bin/env python3

# Script para configurar la hora de nuestro dispositivo con la de una máquina víctima


import time
import re
import os
import subprocess
import pickle
import argparse
from pwn import * 
from datetime import datetime


BACKUP_FILE = 'timezone_backup.pkl' 


def get_system_date():
    
    try:
        
        result = subprocess.run(
                ['date'],
                capture_output=True,
                text=True,
                timeout=10
                )

        local_time = result.stdout.strip()
        
        p1 = log.progress('Formateando la fecha de tu sistema')
        time.sleep(2)

        try:

            month_mapping = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", 
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

            parts = local_time.split()

            if len(parts) >= 6:
                month_abbr = parts[1]
                day = parts[2]
                time_12h = parts[3]
                am_pm = parts[4]
                year = parts[5] if len(parts) == 6 else parts[6]

                
                month_num = month_mapping.get(month_abbr, "00")

                time_24h = datetime.strptime(f'{time_12h} {am_pm}', '%I:%M:%S %p').strftime('%H:%M:%S')

                return f'{year}-{month_num}-{day} {time_24h}'



        except ValueError:
            return local_time

        if result.returncode == 0:
            print(f'\n\t[+] La fecha y hora de tu sistema es {result.stdout}\n')

        else:
            print(f'[!] Ocurrió un error recopilando la fecha y hora de tu sistema...\n')

    except subprocess.TimeoutExpired:
        print(f'\n[!] Hemos sobrepasado el timepo intentando obtener la fecha y hora de tu sistema...\n')

    except Exception as e:
        print(f'\n[!] Ocurrió un error inesperado...\n')

def get_victim_date(target):
    try:


        p2 = log.progress("Recopilando la fecha y hora de la victima")
        time.sleep(2)
        result = subprocess.run(
                ['ntpdate', '-q', target],
                capture_output=True,
                text=True,
                timeout=10
                )

        if result.returncode == 0:
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', result.stdout)
            if match:
                return match.group(1)

            else:
                print(f'\n[!] No se pudo obtener la hora')
            print(f'\n\t[+] La fecha y hora de la victima es {result.stdout}')
        else:
            print(f'\n[!] Error al obtener la hora de la víctima... {result.stderr.strip()}\n')
    except subprocess.TimeoutExpired:
        print(f'\n[!] Hemos sobrepasado el tiempo intentado obtener información de {target}...\n')

    except Exception as e:
        print(f'\n[!] Error inesperado {e}\n')


def backup_timezone():

    backup_data = {}

    try:

        result = subprocess.run(
                ['timedatectl', 'show', '--property=Timezone', '--value'],
                check=True,
                capture_output=True,
                text=True
                )

        backup_data['system_timezone'] = result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):

        backup_data['system_timezone'] = None

        print(f'[!] No se pudo obtener la zona horaria de tu máquina... Saliendo... [!]')
        sys.exit(1)


    backup_data['env_tz'] = os.environ.get('TZ')

    
    with open(BACKUP_FILE, 'wb') as f:
        
        pickle.dump(backup_data, f)

    print(f"\n[+] Zona de respaldo guardada. Sistema: {backup_data['system_timezone']}.")
    if backup_data['env_tz']:
        print(f"\n[+] Variable de entorno TZ: {backup_data['env_tz']}")
    else:
        print(f'\n[+] No existe la variable de entorno TZ.')

def check_backup():
    """
    Check if backup file exists and display its information
    """
    try:
        if os.path.exists(BACKUP_FILE):
            file_stat = os.stat(BACKUP_FILE)
            file_size = file_stat.st_size
            file_mtime = file_stat.st_mtime
            
            print(f"[+] Backup file found: {BACKUP_FILE}")
            print(f"    Size: {file_size} bytes")
            print(f"    Last modified: {file_mtime}")
            
            # Optional: Read backup metadata
            try:
                with open(BACKUP_FILE, 'rb') as f:
                    backup_data = pickle.load(f)
                print(f"    Timezone: {backup_data.get('system_timezone', 'Unknown')}")
                print(f"    Backup timestamp: {backup_data.get('backup_timestamp', 'Unknown')}")
            except Exception as e:
                print(f"    Could not read backup content: {e}")
        else:
            print(f"[-] Backup file not found: {BACKUP_FILE}")
            
    except Exception as e:
        print(f'[!] Error checking backup: {e}')


def restore_timezone():
    try:    

        with open(BACKUP_FILE,'rb') as f:
            
            backup_data = pickle.load(f)

    except FileNotFoundError:

        print(f'[!] No se encontró el respaldo de tu zona horaria...')

    if backup_data.get('system_timezone'):
        try:    

            subprocess.run(
                    ['sudo', 'timedatectl', 'set-timezone', backup_data['system_timezone']],
                    check=True
                    )
            print(f"\n[+] Zona horaria del sistema restaurada a: {backup_data['system_timezone']}")


        except subprocess.CalledProcessError:

            print(f'\n[!] Ocurrió un error al intentar restaurar tu zona horaria...')

    
    new_tz = backup_data['env_tz']


    if new_tz is not None:
        os.environ['TZ'] = new_tz

        print(f'\n[+] Variable de entorno de zona horaria reestablecida a: {new_tz}.')
    
    else:
        if 'TZ' in os.environ:
            del os.environ['TZ']
            print(f'\n[+] Variable de entorno TZ eliminada (no existía en el backup)')


        else:
            print(f'\n[+] No existía variable de entorno en el backup, no se requieren acciones.')


def get_ntp_hour(server=None):
    """
    Obtiene la hora exacta usando servidores NTP públicos.
    Retorna la hora en formato 'YYYY-MM-DD HH:MM:SS' o None si falla.
    """
    if server is None:
        server = [
            'pool.ntp.org',
            'time.google.com', 
            'time.windows.com',
            'ntp.ubuntu.com'
        ]
    
    for servidor in server:
        try:
            print(f"[+] Intentando con servidor NTP: {servidor}")
            
            resultado = subprocess.run(
                ['ntpdate', '-q', servidor],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                # Extraer la fecha y hora del output de ntpdate
                patron = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                coincidencia = re.search(patron, resultado.stdout)
                
                if coincidencia:
                    hora_ntp = coincidencia.group(1)
                    print(f"[+] Hora obtenida de {servidor}: {hora_ntp}")
                    return hora_ntp
            else:
                print(f"[!] Error con {servidor}: {resultado.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print(f"[!] Timeout con {servidor}")
        except Exception as e:
            print(f"[!] Error inesperado con {servidor}: {e}")
    
    return None


def restore_time():
    """
    Restaura la hora del sistema usando NTP como método principal
    y método manual como respaldo, manteniendo el ajuste de día -1.
    """
    try:
        print("[+] Iniciando restauración de hora...")
        
        # 1. PRIMERO INTENTAR CON NTP
        hora_ntp = get_ntp_hour()
        
        if hora_ntp:
            print(f"[+] Hora exacta obtenida via NTP: {hora_ntp}")
            
            respuesta = input("[?] ¿Restaurar la hora con esta fecha? (Y/n): ").strip().lower()
            
            if respuesta in ['y', 'yes', '']:
                subprocess.run(
                    ['sudo', 'date', '-s', hora_ntp],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                print(f"[✓] Hora restaurada exitosamente via NTP: {hora_ntp}")
                return True
            else:
                print("[!] Restauración NTP cancelada por el usuario")
                # Continuar con método manual
        else:
            print("[!] No se pudo obtener hora via NTP")
        
        # 2. MÉTODO MANUAL (RESPALDO) - Manteniendo tu lógica original
        print("[+] Usando método manual de restauración...")
        month_mapping = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", 
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Obtener fecha actual del sistema
        result = subprocess.run(
            ['date'],
            check=True,
            capture_output=True,
            timeout=10,
            text=True
        )

        hora_actual = result.stdout.strip()
        userResponse = input(f'\n[+] La hora actual de tu sistema es: {hora_actual}? (Y/N) ')
        
        splittedTime = result.stdout.split()
        if len(splittedTime) >= 6:
            month_abbr = splittedTime[1]
            day = splittedTime[2]
            time_12h = splittedTime[3]
            am_pm = splittedTime[4]
            year = splittedTime[5]

            month_num = month_mapping.get(month_abbr, '00')
            day = int(day) - 1  # Manteniendo tu ajuste específico
            time_24h = datetime.strptime(f'{time_12h} {am_pm}', '%I:%M:%S %p').strftime('%H:%M:%S')

            restored_date = f'{year}-{month_num}-{day} {time_24h}'

            if userResponse.strip().lower() == 'y':
                subprocess.run(
                    ['sudo', 'date', '-s', restored_date],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                print(f'\n[✓] Hora restaurada exitosamente a: {restored_date}')
                return True
                
            elif userResponse.strip().lower() == 'n':
                while True:
                    userInputDate = input(f'\n[+] Introduce la fecha manualmente (YYYY-MM-DD HH:MM:SS): ')
                    
                    # Validar formato básico
                    if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', userInputDate):
                        subprocess.run(
                            ['sudo', 'date', '-s', userInputDate],
                            check=True,
                            capture_output=True,
                            timeout=10
                        )
                        print(f'\n[✓] Hora restaurada exitosamente a: {userInputDate}')
                        return True
                    else:
                        print("[!] Formato inválido. Usa: YYYY-MM-DD HH:MM:SS")
            else:
                print(f'\n[!] Opción no válida. Saliendo...')
                return False
        else:
            print("[!] No se pudo parsear la fecha del sistema")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f'\n[!] Error al ejecutar comando: {e}')
        if hasattr(e, 'stderr') and e.stderr:
            print(f'[!] Detalles: {e.stderr.decode().strip()}')
        return False
    except ValueError as e:
        print(f'\n[!] Error en formato de fecha: {e}')
        return False
    except Exception as e:
        print(f'\n[!] Error inesperado: {e}')
        return False



def get_root():
    
    if os.getuid() == 0:
        return True
    else:
        print(f'\n[!] Debes ser root para ejecutar esta herramienta\n')
        sys.exit(1)

def calculate_and_synchronize(local_time, victim_time):
    """
    Calcula diferencias y sincroniza horarios
    Retorna: True si fue exitoso, False si falló
    """
    try:
        time_format = "%Y-%m-%d %H:%M:%S"
        
        # Calcular diferencia
        local_dt = datetime.strptime(local_time, time_format)
        victim_dt = datetime.strptime(victim_time, time_format)
        
        difference = victim_dt - local_dt
        total_seconds = difference.total_seconds()
        
        print(f'[+] Diferencia detectada: {total_seconds/3600:.2f} horas')
        
        # Sincronizar
        result = subprocess.run(
            ['sudo', 'date', '-s', victim_time],
            check=True,
            capture_output=True,
            timeout=10
        )
        
        print(f'[✓] Hora cambiada exitosamente a: {victim_time}')
        return True
        
    except subprocess.CalledProcessError as e:
        print(f'[!] Error al cambiar hora: {e.stderr.decode().strip()}')
        return False
    except ValueError as e:
        print(f'[!] Error en formato de fecha: {e}')
        return False
    except Exception as e:
        print(f'[!] Error inesperado: {e}')
        return False


def parser_args():

    parser = argparse.ArgumentParser(description='Script para configurar la hora con una máquina víctima')
    parser.add_argument('-t', '--target', dest='target', help='Objetivo para configurar la hora')
    parser.add_argument('-r', '--restore', action='store_true', help='Restaurar la zona horaria')
    parser.add_argument('--target-time', help='Establece una hora específica (formato: YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--check-backup', action='store_true', help='Ver si el backup que se tiene es reciente o es antiguo')
    
    return parser.parse_args()


def main():
    """
    Función principal mejorada para gestionar la sincronización horaria
    """
    # 1. Verificar permisos primero
    get_root()
    
    # 2. Parsear argumentos
    args = parser_args()
    
    # 3. Manejar argumentos especiales primero
    if hasattr(args, 'check_backup') and args.check_backup:
        check_backup()
        return
    
    # 4. Modo restauración - manejar primero y salir
    if args.restore:
        print("[+] Modo restauración activado")
        restore_time()      # Restaurar hora del sistema
        restore_timezone()  # Restaurar zona horaria
        return
    
    # 5. MODO NORMAL: Sincronización
    print("[+] Iniciando proceso de sincronización horaria")
    
    # Crear backup ANTES de cualquier cambio
    backup_timezone()
    
    # Deshabilitar NTP para evitar que revierta nuestros cambios
    try:
        subprocess.run(
            ['sudo', 'timedatectl', 'set-ntp', 'false'],
            check=True,
            capture_output=True,
            timeout=10
        )
        print("[+] Sincronización NTP deshabilitada temporalmente")
    except subprocess.CalledProcessError as e:
        print(f'[!] Error al deshabilitar NTP: {e.stderr.decode().strip()}')
        return
    except subprocess.TimeoutExpired:
        print('[!] Timeout al deshabilitar NTP')
        return
    
    # Obtener horas para sincronización
    local_time = get_system_date()
    
    # Validar que tenemos un objetivo
    if not args.target and not args.target_time:
        print('[!] Debes especificar un objetivo (--target) o una hora manual (--target-time)')
        return
    
    # Obtener hora objetivo
    victim_time = None
    if args.target:
        victim_time = get_victim_date(args.target)
    elif args.target_time:
        victim_time = args.target_time
    
    # Verificar que tenemos ambas horas
    if not local_time or not victim_time:
        print('[!] No se pudieron obtener las horas necesarias para la sincronización')
        return
    
    # Mostrar información
    print(f'\n[+] Hora del sistema local: {local_time}')
    print(f'[+] Hora objetivo: {victim_time}')
    
    # Realizar sincronización
    success = calculate_and_synchronize(local_time, victim_time)
    
    if success:
        print("[✓] Sincronización completada exitosamente")
    else:
        print("[!] La sincronización falló")



if __name__ == '__main__':
    main()
