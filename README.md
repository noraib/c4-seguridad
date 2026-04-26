# Proyecto Seguridad de la información
En este repositorio se pueden encontrar dos carpetas:
 - Entrega1-botones: es el entregable que hicimos al principio de la asignatura.
 - Proyecto_esteganografía: es el código del proyecto final de la asignatura.

## Sistema de Cripto-Esteganografía
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
📁 Proyecto_esteganografia/
│
├── main.py                     # Punto de entrada y menú interactivo del sistema.
├── 📁 src/                     
│   ├── 📁 cripto/              # Módulos de cifrado AES (externo/dependencias).
│   ├── 📁 esteganografia/      # Módulos de manipulación de LSB (externo/dependencias).
│   ├── 📁 gan/                 # Scripts de generación de imágenes.
│   ├── extraer.py              # Lógica para recuperar y descifrar mensajes.
│   ├── ocultar.py              # Lógica para cifrar y ocultar mensajes.
│   ├── procesador_masivo.py    # Script para procesar lotes de imágenes y CSVs.
│   ├── proteger_csv.py         # Sistema de "Caja Fuerte" con Fernet.
│   ├── test_aes.py             # Main de prueba para probar encriptación y decriptación.
│   ├── test_aes+esteg.py       # Main de prueba para probar la integración de la encriptación y decriptación con la inserción en imágenes.
│   └── utils.py                # Utilidades compartidas
└── 📁 media_cripto_esteg/      # Carpetas generadas automáticamente para inputs, outputs y archivos csv.
```



## Requisitos y Dependencias

Para que el proyecto funcione correctamente, necesitas tener instalado **Python 3** y las además:

El fichero `uv.lock` garantiza que todas las personas que ejecuten el proyecto usen exactamente las mismas versiones de las librerías.

#### Requisitos previos

Tener `uv` instalado. Si no lo tienes:

```bash
# En Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# En Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Instalación de dependencias

Desde la carpeta `proyecto_esteganografia`, ejecuta:

```bash
uv sync
```

Este comando lee el fichero `uv.lock` y crea un entorno con las versiones exactas de las librerías necesarias.


Además se debe instalar la siguiente librería **Tkinter** (Para la selección de archivos con interfaz gráfica):

- En sistemas basados en Debian/Ubuntu: 

```bash
sudo apt install python3-tk
```


---

## Cómo usarlo

1.  Clona o descarga este repositorio en tu máquina local.
2.  Abre una terminal y navega hasta el directorio raíz del proyecto, es decir, hasta **"Proyecto_esteganografia"**.
3.  Conectate al entorno virtual creado con uv.
4.  Ejecuta el menú principal:

    ```bash
    python main.py
    ```
5.  Aparecerá el menú interactivo. Simplemente introduce el número de la opción que deseas ejecutar y sigue las instrucciones en pantalla.


---

## Funcionalidades incluidas


### 1. Generación de Imágenes (GAN)
El sistema utiliza una Red Neuronal Generativa (GAN) para crear imágenes de barcos desde cero. Estas imágenes son ideales para la esteganografía porque, al ser sintéticas, no existe una "imagen original" en internet con la que un analista pueda comparar para detectar alteraciones en los píxeles.

### 2. Ocultar y Extraer (El núcleo)
* **Cifrado:** Antes de ocultar nada, el texto se cifra con **AES-256** en modo Fernet. Esto garantiza que aunque alguien sospeche que hay algo en la imagen y logre extraer los bits, solo verá datos aleatorios.
* **Inserción LSB:** El mensaje cifrado se descompone en bits. Estos bits sustituyen el último bit de los canales Rojo, Verde y Azul de cada píxel. 

### 3. Procesamiento Masivo
Diseñado para flujos de trabajo de datos. 
- **Entrada:** Un archivo `CSV` con una lista de textos (ej. chistes).
- **Acción:** El sistema toma una imagen única de la carpeta GAN para cada texto, realiza el proceso de cifrado/ocultación y guarda el resultado.
- **Salida:** Una carpeta con imágenes esteganográficas y un `reporte_claves_final.csv` que vincula cada imagen con su clave de descifrado.

### 4. Caja Fuerte
Para evitar que el archivo de claves (`reporte_claves_final.csv`) caiga en manos equivocadas, este módulo permite:
- **Bloquear:** Cifra el CSV completo usando una **Contraseña Maestra** definida por el usuario.
- **Desbloquear:** Restaura el acceso al CSV original.
- **Detección de estado:** El sistema detecta automáticamente si el archivo ya está cifrado para evitar el "doble cifrado" que corrompería los datos.
- **Obtener chiste:** Obtiene el chiste almacenado en una de las imágenes procesadas masivamente.
---

## Especificaciones Técnicas

### El Algoritmo LSB (Least Significant Bit)
La modificación del bit menos significativo es una técnica donde el cambio en el valor del color es de máximo **1 unidad** (sobre 255). 

### Seguridad Criptográfica
- **Cifrado de Mensajes:** AES-256 (Fernet).
- **Derivación de Clave Maestra:** Se utiliza **PBKDF2HMAC** con SHA256 y un *salt* de 100,000 iteraciones para transformar tu contraseña simple en una clave criptográfica robusta.

---

## Directorios de interés

El sistema organiza automáticamente tus archivos en la carpeta `media_cripto_esteg/`:
* `output/`: Aquí aparecerán tus imágenes con mensajes ocultos (`stego_result.png`).
* `procesado_masivo/`: Contiene los reportes de claves y las imágenes generadas masivamente.

---


## Notas Importantes

* **Contraseña Maestra:** Si utilizas la opción de *Caja Fuerte*, asegúrate de recordar tu contraseña maestra, ya que una contraseña olvidada resultará en la pérdida del archivo CSV cifrado.