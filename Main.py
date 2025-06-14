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
    
