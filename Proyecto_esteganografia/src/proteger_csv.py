import os
import csv
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from src.utils import select_file
from src.cripto.aes import decrypt_message
from src.esteganografia.lsb import decode_lsb

def obtener_llave(password: str):
    """Genera la llave maestra necesaria para transformar los datos."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'sal_fija_para_clase', # Importante: no cambiar esto para poder recuperar datos
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def esta_bloqueado(ruta_archivo):
    """
    Comprueba si el archivo CSV está cifrado (bloqueado) o en claro (desbloqueado).
    Un token Fernet siempre empieza por 'gAAAAA' (byte de versión 0x80 + timestamp).
    Un CSV en claro empieza por la cabecera 'id_chiste,...'.
    Devuelve True si está bloqueado, False si está desbloqueado.
    """
    try:
        with open(ruta_archivo, "rb") as f:
            inicio = f.read(6)
        return inicio == b"gAAAAA"
    except Exception:
        return False

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
        return True
    except Exception:
        print("\n❌ ERROR: Contraseña incorrecta o el archivo ya está en ese estado.")
        return False


def cambiar_estado_csv(ruta_archivo,modo):
    """Lee, transforma y sobrescribe el archivo original."""
    if not os.path.exists(ruta_archivo):
        print(f"❌ No se encuentra el archivo a bloquear. \nPrimero debes generarlo (función 4)")
        return

    # Si está bloqueado, solo se puede desbloquear u obtener
    if esta_bloqueado(ruta_archivo) and modo == "bloquear":
        print("\n⛔ El archivo está BLOQUEADO. Primero debes desbloquearlo (opción 2).")
        return

    # Si está desbloqueado, solo se puede bloquear
    if not esta_bloqueado(ruta_archivo) and modo == "desbloquear":
        print("\n⛔ El archivo está DESBLOQUEADO. Primero debes bloquearlo (opción 1).")
        return



    try:
        # 1. Leer el contenido actual del CSV (sea texto o cifrado)
        with open(ruta_archivo, "rb") as f:
            datos_actuales = f.read()

        # 2. Aplicar la transformación
        if modo == "bloquear":
            password = input("Introduce la Contraseña Maestra: ")
            # Antes de desbloquear, comprobar que se ha introducido una clave
            if not password:
                print("\n⛔ Debes introducir una contraseña.")
                return
            llave = obtener_llave(password)
            fernet = Fernet(llave)
            bloquear(fernet, datos_actuales, ruta_archivo)
            
        elif modo == "desbloquear":
            # --- PUNTO 4: Reintentos para evitar que el archivo quede bloqueado por olvido ---
            password = input("Introduce la Contraseña Maestra: ")
            # Antes de desbloquear, comprobar que se ha introducido una clave
            if not password:
                print("\n⛔ Debes introducir una contraseña.")
                return
            llave = obtener_llave(password)
            fernet = Fernet(llave)
            MAX_INTENTOS = 3
            exito = desbloquear(fernet, datos_actuales, ruta_archivo)
            intentos = 1
            while not exito and intentos < MAX_INTENTOS:
                restantes = MAX_INTENTOS - intentos
                print(f"   Te quedan {restantes} intento(s).")
                nueva_pwd = input("Introduce la Contraseña Maestra de nuevo: ")
                if not nueva_pwd:
                    print("\n⛔ Debes introducir la contraseña.")
                    intentos += 1
                    continue
                fernet = Fernet(obtener_llave(nueva_pwd))
                exito = desbloquear(fernet, datos_actuales, ruta_archivo)
                intentos += 1
            if not exito:
                print("\n⚠️  Se agotaron los 3 intentos. El archivo sigue BLOQUEADO pero intacto.")
                print("    Volviendo al menú...")
            
        else: 
            # Obtener y mostrar el chiste descifrado
            # 1. Desbloquear el CSV temporalmente
            if esta_bloqueado(ruta_archivo):
                password = input("Introduce la Contraseña Maestra: ")
                # Antes de desbloquear, comprobar que se ha introducido una clave
                if not password:
                    print("\n⛔ Debes introducir una contraseña.")
                    return
                llave = obtener_llave(password)
                fernet = Fernet(llave)
                
                if not desbloquear(fernet, datos_actuales, ruta_archivo):
                    return  # contraseña incorrecta, el CSV sigue bloqueado intacto

            # 2. Pedir al usuario la imagen estego
            path = select_file("Elige la imagen de la que quieres obtener el chiste:")
            if not path:
                print("❌ No se seleccionó ninguna imagen.")
                # Volvemos a bloquear con los datos en claro (los que acabamos de escribir)
                with open(ruta_archivo, "rb") as f:
                    datos_claros = f.read()
                bloquear(fernet, datos_claros, ruta_archivo)
                return

            nombre_archivo = os.path.basename(path)

            # 3. Buscar la clave AES correspondiente en el CSV
            clave_hex = None
            try:
                with open(ruta_archivo, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for fila in reader:
                        if fila['imagen_estego'] == nombre_archivo:
                            clave_hex = fila['clave_aes_hex']
                            break

                # 4. Extraer y descifrar el chiste de la imagen
                if clave_hex:
                    try:
                        clave_aes = bytes.fromhex(clave_hex)
                        ciphertext = decode_lsb(path)
                        chiste = decrypt_message(ciphertext, clave_aes)
                        print(f"\nChiste de {nombre_archivo}:")
                        print(f"   {chiste}")
                    except Exception as e:
                        print(f"❌ Error al descifrar la imagen: {e}")
                else:
                    print(f"❌ No se encontró una clave para el archivo: {nombre_archivo}")

            except FileNotFoundError:
                print("Error: No se encontró el archivo CSV de base de datos.")

            finally:
                # 5. Volver a bloquear el CSV con los datos en claro (no con ciphertext)
                with open(ruta_archivo, "rb") as f:
                    datos_claros = f.read()
                
                if not esta_bloqueado(ruta_archivo):
                    password = input("Introduce la Contraseña Maestra: ")
                    # Antes de desbloquear, comprobar que se ha introducido una clave
                    if not password:
                        print("\n⛔ Debes introducir una contraseña.")
                        return
                    llave = obtener_llave(password)
                    fernet = Fernet(llave)
                    
                    if not bloquear(fernet, datos_claros, ruta_archivo):
                        return  # contraseña incorrecta, el CSV sigue bloqueado intacto

                
    except FileNotFoundError:
                print("Error: No se encontró el archivo CSV de base de datos.")