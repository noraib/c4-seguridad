# Sistema de Cripto-Esteganografía
Este proyecto es una herramienta interactiva de línea de comandos (CLI) diseñada para ocultar y proteger información confidencial dentro de imágenes. Combina técnicas de **Esteganografía** (modificación del bit menos significativo - LSB) y **Criptografía** (cifrado AES) para asegurar que los mensajes no solo sean invisibles, sino también indescifrables sin la clave correcta.

## Características Principales

El sistema se opera a través de un menú principal (`main.py`) que ofrece las siguientes funcionalidades:

* **Generación de Imágenes**: Integración con un modelo GAN para crear imágenes base de **barcos**.
* **Ocultar Mensajes (Cifrado + Esteganografía)**: Permite al usuario escribir un mensaje, cifrarlo con AES y ocultarlo en una imagen seleccionada gráficamente.
* **Extraer Mensajes (Descifrado + Esteganografía)**: Recupera un mensaje oculto de una imagen y lo descifra utilizando la clave hexadecimal proporcionada.
* **Procesamiento Masivo**: Automatiza la ocultación de múltiples textos (en este caso, **chistes** desde un `CSV`) en un lote de imágenes generadas, creando otro archivo `CSV` con las claves asociadas.
* **Caja Fuerte (Protección de CSV)**: Un sistema de seguridad adicional que cifra el archivo de claves con una contraseña maestra, permitiendo bloquear, desbloquear o consultar claves de forma segura.



## Estructura del Proyecto

```text
📁 tu_proyecto/
│
├── main.py                     # Punto de entrada y menú interactivo del sistema.
├── 📁 src/                     
│   ├── extraer.py              # Lógica para recuperar y descifrar mensajes.
│   ├── ocultar.py              # Lógica para cifrar y ocultar mensajes.
│   ├── procesador_masivo.py    # Script para procesar lotes de imágenes y CSVs.
│   ├── proteger_csv.py         # Sistema de "Caja Fuerte" con Fernet.
│   ├── utils.py                # Utilidades compartidas
│   └── 📁 gan/                 # Scripts de generación de imágenes.
│
├── 📁 cripto/                  # Módulos de cifrado AES (externo/dependencias).
├── 📁 esteganografia/          # Módulos de manipulación de LSB (externo/dependencias).
└── 📁 media_cripto_esteg/      # Carpetas generadas automáticamente para inputs, outputs y archivos csv.
```



## Requisitos y Dependencias

Para que el proyecto funcione correctamente, necesitas tener instalado **Python 3** y las siguientes bibliotecas:

1.  **Tkinter** (Para la selección de archivos con interfaz gráfica):
    * En sistemas basados en Debian/Ubuntu: 
        ```bash
        sudo apt install python3-tk
        ```
2.  **Paquetes de Python** instalables a través de:
```bash
uv sync
```

---

## Cómo usarlo

1.  Clona o descarga este repositorio en tu máquina local.
2.  Abre una terminal y navega hasta el directorio raíz del proyecto, es decir, hasta **"Proyecto_esteganografia"**.
3.  Ejecuta el menú principal:

    ```bash
    python main.py
    ```
4.  Aparecerá el menú interactivo. Simplemente introduce el número de la opción que deseas ejecutar y sigue las instrucciones en pantalla.

---

## Notas Importantes

* **Contraseña Maestra:** Si utilizas la opción de *Caja Fuerte*, asegúrate de recordar tu contraseña maestra, ya que una contraseña olvidada resultará en la pérdida del archivo CSV cifrado.