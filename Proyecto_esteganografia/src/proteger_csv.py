import os
import csv
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from src.utils import select_file

def obtener_llave(password: str):
    """Genera la llave maestra necesaria para transformar los datos."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'sal_fija_para_clase', # Importante: no cambiar esto para poder recuperar datos
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def bloquear(fernet, datos_actuales, ruta_archivo):
    try:
        # Convertimos el texto en 'basura' ilegible
        datos_nuevos = fernet.encrypt(datos_actuales)
        confirmacion = "🔒 ARCHIVO BLOQUEADO: Ahora el CSV es ilegible."
                
        # 3.A SOBRESCRITURA: Guardamos los nuevos datos en el MISMO archivo
        with open(ruta_archivo, "wb") as f:
            f.write(datos_nuevos)
        print(f"\n✅ {confirmacion}")

    except Exception:
        print("\n❌ ERROR: Contraseña incorrecta o el archivo ya está en ese estado.")

def desbloquear(fernet, datos_actuales, ruta_archivo):
    try:
        # Convertimos la 'basura' de vuelta a texto claro
        datos_nuevos = fernet.decrypt(datos_actuales)
        confirmacion = "🔓 ARCHIVO DESBLOQUEADO: El CSV vuelve a ser legible."
                
        # 3.A SOBRESCRITURA: Guardamos los nuevos datos en el MISMO archivo
        with open(ruta_archivo, "wb") as f:
            f.write(datos_nuevos)
        print(f"\n✅ {confirmacion}")
    except Exception:
        print("\n❌ ERROR: Contraseña incorrecta o el archivo ya está en ese estado.")


def cambiar_estado_csv(ruta_archivo, password, modo):
    """Lee, transforma y sobrescribe el archivo original."""
    if not os.path.exists(ruta_archivo):
        print(f"❌ No se encuentra el archivo: {ruta_archivo}")
        return

    llave = obtener_llave(password)
    fernet = Fernet(llave)

    try:
        # 1. Leer el contenido actual del CSV (sea texto o cifrado)
        with open(ruta_archivo, "rb") as f:
            datos_actuales = f.read()

        # 2. Aplicar la transformación
        if modo == "bloquear":
            bloquear(fernet, datos_actuales, ruta_archivo)
            
        elif modo == "desbloquear":
            desbloquear(fernet, datos_actuales, ruta_archivo)
            
        else: 
            # Primero se abre
            desbloquear(fernet, datos_actuales, ruta_archivo)
            
            # Luego se obtiene la clave
            path = select_file("Elige de que archivo se quiere obtener la clave: ")
            nombre_archivo = os.path.basename(path)

            clave_encontrada = None

            ## Abrir y buscar en el CSV
            try:
                with open(ruta_archivo, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for fila in reader:
                        if fila['imagen_estego'] == nombre_archivo:
                            clave_encontrada = fila['clave_aes_hex']
                            break

                ## Resultado
                if clave_encontrada:
                    print(f"✅ Clave encontrada para {nombre_archivo}:")
                    print(clave_encontrada)
                else:
                    print(f"❌ No se encontró la clave para el archivo: {nombre_archivo}")

            except FileNotFoundError:
                print("Error: No se encontró el archivo CSV de base de datos.")
            
            finally:
                bloquear(fernet, datos_actuales, ruta_archivo)
                
    except FileNotFoundError:
                print("Error: No se encontró el archivo CSV de base de datos.")