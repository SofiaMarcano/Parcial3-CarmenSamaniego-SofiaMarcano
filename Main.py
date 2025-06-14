import os
def rev_num(msj):
    while True:
        try:
            x=int(input(msj))
            return x
        except ValueError:
            print("Ingrese un numero entero")
        
        
while True:
    print('''###MENU###
               1. Procesar archivos DICOM
               2. Ingresar paciente
               3. Procesar imagenes JPG o PNG
               4. Trasladar imagen y guardar
               5. Binarización, transformacion y dibujo de imagen
               6. Salir''')
    Menu=rev_num("SEleccione una opcion")
    
# Diccionario global donde se almacenan los DICOM procesados
diccionario_archivos= {}

def proc_dicom():
    clave = input("Ingrese una clave única para este conjunto DICOM (ej. paciente1): ")
    if clave in dicccionario_archivos:
        print("Esa clave ya existe.")
        return
    carpeta = input("Ingrese la ruta a la carpeta que contiene los archivos DICOM: ")
    if not os.path.isdir(carpeta):
        print("La ruta ingresada no es válida.")
        return
    try:
        dicom_obj = DICOMC(carpeta)
        volumen = dicom_obj.cargar_dicom_y_reconstruir()
        if volumen is not None:
            diccionario_archivos[clave] = dicom_obj
            print(f"DICOM procesado y guardado con clave '{clave}'")
            print(f"Dimensiones del volumen reconstruido: {volumen.shape}")
        else:
            print("No se pudo reconstruir el volumen.")
    except Exception as e:
        print("Error procesando el DICOM:", e)
# Diccionario global para pacientes
pacientes={}
def create_paciente():
    if not diccionario_archivos:
        print("No hay archivos DICOM procesados.")
        return

    print("\nDICOMs disponibles:")
    claves = list(diccionario_archivos.keys())
    for i, clave in enumerate(claves):
        print(f"{i + 1}. {clave}")
    indice = rev_num("Ingrese el número del DICOM que quiere usar para crear el paciente: ") - 1
    if indice < 0 or indice >= len(claves):
        print("Índice inválido.")
        return
    clave = claves[indice]
    dicom_obj = diccionario_archivos[clave]
    # Obtener datos del paciente y volumen reconstruido
    nombre, edad, id_paciente = dicom_obj.obt_info()
    volumen = dicom_obj.volumen
    if volumen is None:
        print("Volumen no reconstruido.")
        return
    paciente = Paciente(nombre, edad, id_paciente, volumen)
    pacientes[clave] = paciente
    print(f"Paciente '{nombre}' creado y almacenado con clave '{clave}'")
