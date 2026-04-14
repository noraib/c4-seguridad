
def select_file(frase):
    """Abre la ventana para elegir el archivo."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()  # Oculta la ventanita negra de fondo
        root.attributes("-topmost", True)  # Fuerza la ventana al frente
        
        print(frase)
        path = filedialog.askopenfilename(
            title="Selecciona la imagen base de tu GAN",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
        )
        root.destroy()
        return path
    except Exception as e:
        print(f"\n[!] No se pudo abrir el selector visual: {e}")
        return input("[?] Introduce la ruta manualmente: ").strip()