import csv
import os
from pathlib import Path
from src.cripto.aes import generate_key, encrypt_message
from src.esteganografia.lsb import encode_lsb

def procesar_mision_esteganografica(csv_entrada, carpeta_gan, carpeta_salida):
    # Configuración de rutas
    Path(carpeta_salida).mkdir(parents=True, exist_ok=True)
    csv_reporte = Path(carpeta_salida) / "reporte_claves_final.csv"
    
    # 1. Leer chistes del CSV de entrada
    chistes = []
    if not os.path.exists(csv_entrada):
        print(f"❌ Error: No se encuentra {csv_entrada}")
        return

    with open(csv_entrada, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        chistes = [row for row in reader]

    # 2. Listar imágenes de la GAN disponibles
    imagenes_disponibles = sorted(list(Path(carpeta_gan).glob("*.png")))
    
    if len(imagenes_disponibles) < len(chistes):
        print(f"⚠️ Alerta: Tienes {len(chistes)} chistes pero solo {len(imagenes_disponibles)} imágenes en la carpeta GAN. Genera más imagenes para poder completar la encriptación.")
        return

    # 3. Procesar y Generar CSV de salida
    print(f"🚀 Procesando lote de {len(chistes)} chistes...")
    
    resultados = []
    
    for i, item in enumerate(chistes):
        chiste_texto = item['chiste']
        img_original = imagenes_disponibles[i]
        
        # Nombre del nuevo archivo con el chiste oculto
        nombre_stego = f"stego_{img_original.name}"
        path_stego = Path(carpeta_salida) / nombre_stego
        
        # --- CIFRADO ---
        key = generate_key()
        mensaje_cifrado = encrypt_message(chiste_texto, key)
        
        # --- ESTEGANOGRAFÍA ---
        try:
            encode_lsb(str(img_original), mensaje_cifrado, str(path_stego))
            
            # Guardar datos para el CSV de salida
            resultados.append({
                "id_chiste": item.get('id', i+1),
                "imagen_estego": nombre_stego,
                "clave_aes_hex": key.hex(),
                "chiste_original": chiste_texto
            })
            print(f"✅ [{i+1}/{len(chistes)}] Ocultado en {nombre_stego}")
        except Exception as e:
            print(f"❌ Error procesando chiste {i+1}: {e}")

    # 4. Escribir el CSV de salida con las KEYs
    with open(csv_reporte, mode='w', newline='', encoding='utf-8') as f_out:
        # Quitamos "chiste_original" de los campos
        campos = ["id_chiste", "imagen_estego", "clave_aes_hex"]
        writer = csv.DictWriter(f_out, fieldnames=campos)
        
        writer.writeheader()
        
        # Filtramos los resultados para no incluir el texto del chiste
        for res in resultados:
            # Creamos una copia sin el chiste para escribirla en el CSV
            fila_segura = {k: res[k] for k in campos}
            writer.writerow(fila_segura)

    print(f"\n✨ PROCESO FINALIZADO ✨")
    print(f"📂 Imágenes guardadas en: {carpeta_salida}")
    print(f"📊 Claves asociadas (protegidas) en: {csv_reporte}")

if __name__ == "__main__":
    # Cambiamos "gan" por "imagenes_esteganografia"
    procesar_mision_esteganografica(
        "chistes_entrada.csv", 
        "imagenes_esteganografia", 
        "media_cripto_esteg/procesado_masivo"
    )