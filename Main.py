import os
import Clases
import cv2
import matplotlib.pyplot as plt
def rev_num(msj):
    while True:
        try:
            x=int(input(msj))
            return x
        except ValueError:
            print("Ingrese un numero entero")
archivos= {}
def proc_dicom():
    clave = input("Ingrese una clave única para este conjunto DICOM (ej. paciente1): ")
    if clave in archivos:
        print("Esa clave ya existe.")
        return
    carpeta = input("Ingrese la ruta a la carpeta que contiene los archivos DICOM: ")
    if not os.path.isdir(carpeta):
        print("La ruta ingresada no es válida.")
        return
    try:
        dicom_obj = Clases.DICOMC(carpeta)
        volumen = dicom_obj.cargar_dicom_y_reconstruir()
        if volumen is not None:
            archivos[clave] = dicom_obj
            print(f"DICOM procesado y guardado con clave '{clave}'")
            print(f"Dimensiones del volumen reconstruido: {volumen.shape}")
        else:
            print("No se pudo reconstruir el volumen.")
    except Exception as e:
        print("Error procesando el DICOM:", e)
# Diccionario global para pacientes
pacientes={}
def create_paciente():
    if not archivos:
        print("No hay archivos DICOM procesados.")
        return

    print("\nDICOMs disponibles:")
    claves = list(archivos.keys())
    for i, clave in enumerate(claves):
        print(f"{i + 1}. {clave}")
    indice = rev_num("Ingrese el número del DICOM que quiere usar para crear el paciente: ") - 1
    if indice < 0 or indice >= len(claves):
        print("Índice inválido.")
        return
    clave = claves[indice]
    dicom_obj = archivos[clave]
    # Obtener datos del paciente y volumen reconstruido
    nombre, edad, id_paciente = dicom_obj.obt_info()
    volumen = dicom_obj.volumen
    if volumen is None:
        print("Volumen no reconstruido.")
        return
    paciente = Clases.Paciente(nombre, edad, id_paciente, volumen)
    pacientes[clave] = paciente
    print(f"Paciente '{nombre}' creado y almacenado con clave '{clave}'")
imagenes={}
def ingresar_imagen():
    clave = input("Ingrese una clave única para la imagen (ej. lesion1): ")
    if clave in imagenes:
        print("Esa clave ya existe. Use otra.")
        return
    ruta = input("Ingrese la ruta al archivo de imagen (.jpg o .png): ")
    if not os.path.isfile(ruta) or not (ruta.endswith(".jpg") or ruta.endswith(".png")):
        print("Ruta inválida o archivo no soportado (debe ser .jpg o .png).")
        return
    try:
        imagen_obj = Clases.ImagenM(ruta)
        imagenes[clave] = imagen_obj
        print(f"Imagen cargada y almacenada con clave '{clave}'")
    except Exception as e:
        print("No se pudo cargar la imagen:", e)
    
def proc_imagen():
    if not imagenes:
        print("No hay imágenes JPG/PNG cargadas. Use primero la opción c.")
        return
    print("\nImágenes disponibles:")
    claves = list(imagenes.keys())
    for i, clave in enumerate(claves):
        print(f"{i + 1}. {clave}")
    indice = rev_num("Seleccione el número de imagen a procesar: ") - 1
    if indice < 0 or indice >= len(claves):
        print("Índice inválido.")
        return
    clave = claves[indice]
    imagen_obj = imagenes[clave]
    print("\n--- ¿Qué desea hacer con la imagen? ---")
    print("1. Solo binarización")
    print("2. Solo transformación morfológica")
    print("3. Solo anotación")
    print("4. Todo el proceso (binarizar + morfología + anotación)")
    print("\nTipos de binarización:")
    binarios = {
        1: "THRESH_BINARY",
        2: "THRESH_BINARY_INV",
        3: "THRESH_TRUNC",
        4: "THRESH_TOZERO",
        5: "THRESH_TOZERO_INV"
    }
    for k, v in binarios.items():
        print(f"{k}. {v}")
    try:
        tipo_bin = rev_num("Seleccione tipo de binarización (1-5): ")
        if tipo_bin not in binarios:
            print("Tipo inválido.")
            return
        umbral = rev_num("Ingrese el umbral (ej. 127): ")
    except ValueError:
        print(" Entrada inválida.")
        return
    imagen_bin = imagen_obj.binarizar(tipo_bin, umbral)
    print("\nTipos de transformación morfológica:")
    morfos = {
        1: "MORPH_OPEN",
        2: "MORPH_CLOSE",
        3: "DILATE",
        4: "ERODE"
    }
    for k, v in morfos.items():
        print(f"{k}. {v}")
    tipo_morfo = rev_num("Seleccione tipo (1-4): ")
    if tipo_morfo not in morfos:
            print("Tipo inválido.")
            return
    kernel_size = rev_num("Ingrese tamaño de kernel (ej. 3, 5, 7): ")
    imagen_morfo = imagen_obj.trans_morfo(imagen_bin, tipo_morfo, kernel_size)
    # Anotar imagen
    print("\nFormas para dibujar:\n1. Rectángulo\n2. Círculo")
    forma = rev_num("Seleccione forma (1: rectángulo, 2: círculo): ")
    if forma not in [1, 2]:
        print("Forma inválida.")
        return
    texto = f"Imagen binarizada\nUmbral: {umbral}, Kernel: {kernel_size}"
    anotada = imagen_obj.anotar_imagen(imagen_morfo, texto, forma=forma)
    # Mostrar imagen final
    plt.imshow(cv2.cvtColor(anotada, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Final")
    plt.axis('off')
    plt.show()
    # Guardar
    nombre_g = f"procesada_{clave}.png"
    cv2.imwrite(nombre_g, anotada)
    print(f"✅ Imagen final guardada como: {nombre_g}")
def main():
    while True:
        print('''###MENU###
                1. Procesar archivos DICOM
                2. Ingresar paciente
                3. Procesar imagenes JPG o PNG
                4. Trasladar imagen y guardar
                5. Binarización, transformacion y dibujo de imagen
                6. Salir''')
        menu=rev_num("SEleccione una opcion")
        if menu==1:
            proc_dicom()
        elif menu==2:
            create_paciente()
        elif menu==3:
            ingresar_imagen()
        elif menu==4:
            trasladar_dicom()
        elif menu==5:
            proc_imagen()
        elif menu==6:
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    main()
    
        
    


