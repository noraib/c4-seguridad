import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def obtener_llave(password: str):
    """Genera la llave maestra necesaria para transformar los datos."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'sal_fija_para_clase', # Importante: no cambiar esto para poder recuperar datos
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

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
            # Convertimos el texto en 'basura' ilegible
            datos_nuevos = fernet.encrypt(datos_actuales)
            confirmacion = "🔒 ARCHIVO BLOQUEADO: Ahora el CSV es ilegible."
        else:
            # Convertimos la 'basura' de vuelta a texto claro
            datos_nuevos = fernet.decrypt(datos_actuales)
            confirmacion = "🔓 ARCHIVO DESBLOQUEADO: El CSV vuelve a ser legible."

        # 3. SOBRESCRITURA: Guardamos los nuevos datos en el MISMO archivo
        with open(ruta_archivo, "wb") as f:
            f.write(datos_nuevos)
        
        print(f"\n✅ {confirmacion}")

    except Exception:
        print("\n❌ ERROR: Contraseña incorrecta o el archivo ya está en ese estado.")

if __name__ == "__main__":
    path_csv = "media_cripto_esteg/procesado_masivo/reporte_claves_final.csv"
    
    print("\n" + "="*30)
    print("   CAJA FUERTE DEL REPORTE")
    print("="*30)
    print("1. Bloquear (Cifrar contenido)")
    print("2. Desbloquear (Descifrar contenido)")
    
    op = input("\nSelecciona una opción: ")
    pwd = input("Introduce la Contraseña Maestra: ")

    if op == "1":
        cambiar_estado_csv(path_csv, pwd, "bloquear")
    elif op == "2":
        cambiar_estado_csv(path_csv, pwd, "desbloquear")
    else:
        print("Opción no válida.")