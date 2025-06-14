import pydicom
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
class Paciente:
    def __init__(self, nombre, edad, id_paciente, imagen_3d):
        self.nombre = nombre
        self.edad = edad
        self.id_paciente = id_paciente
        self.imagen_3d = imagen_3d  # matriz 3D reconstruida del DICOM

    def __str__(self):
        return f"Paciente {self.nombre} (ID: {self.id_paciente}, Edad: {self.edad})"
    # def getImagen(self):
    #     return self.imagen_3d
class DICOMC:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.volumen = None
        self.meta_info = None
    def cargar_dicom_y_reconstruir(self):
        arc = sorted([os.path.join(self.carpeta, f) for f in os.listdir(self.carpeta) if f.endswith(".dcm")])
        imagenes = []
        for i in arc:
            ds = pydicom.dcmread(i)
            imagenes.append(ds.pixel_array)
            if self.meta_info is None:
                self.meta_info = ds  # Guardamos un solo archivo con metadata
        self.volumen = np.stack(imagenes, axis=0)
        return self.volumen
    def obt_info(self):
        if self.meta_info:
            nombre = self.meta_info.get('PatientName', 'Desconocido')
            edad = self.meta_info.get('PatientAge', '00Y')
            id_paciente = self.meta_info.get('PatientID', '0000')
            return str(nombre), int(edad[:-1]), str(id_paciente)
        return "Anonimo", 0, "0000"
    def traslacion(self, valor):
        tx = 0
        ty = 0
        if valor == 1:
            tx = 300
            ty = 0
        elif valor == 2:
            tx = -300
            ty = 0
        elif valor ==3:
            tx = 500
            ty = 500
        elif valor == 4:
            tx = 0
            ty = 400
        else:
            tx = 0
            ty = 0
            print(valor)
        corte= pydicom.dcmread(r"datosDICOM\000000.dcm")
        imagen = corte.pixel_array

        MT = np.float32([[1, 0, tx], [0, 1, ty]])
        row,col= imagen.shape
        #Traslación
        tras = cv2.warpAffine(imagen,MT,(col,row))

        plt.imshow(tras, cmap=plt.cm.bone)
        plt.show() 
        
        
            
            # print("\nValores de traslación predefinidos:")
            # print("1. Traslación derecha (30, 0)")
            # print("2. Traslación izquierda (-30, 0)")
            # print("3. Traslación diagonal (50, 50)")
            # print("4. Traslación vertical (0, 40)")

            # #Rotación
            # rot = cv2.warpAffine(img,MR,(col,row))

            # print ('Tamanho ', np.shape(rot))
            # plt.imshow(rot)
            # plt.axis('off')


class ImagenHandler:
    def __init__(self, ruta):
        self.ruta = ruta
        self.imagen = cv2.imread(ruta)
        if self.imagen is None:
            raise ValueError("No se pudo cargar la imagen.")

    def binarizar(self, tipo, umbral=127, max_val=255):
        tipos = {
            1: cv2.THRESH_BINARY,
            2: cv2.THRESH_BINARY_INV,
            3: cv2.THRESH_TRUNC,
            4: cv2.THRESH_TOZERO,
            5: cv2.THRESH_TOZERO_INV
        }
        tipo_cv = tipos.get(tipo)
        _, resultado = cv2.threshold(cv2.cvtColor(self.imagen, cv2.COLOR_BGR2GRAY), umbral, max_val, tipo_cv)
        return resultado

    def trans_morfo(self, imagen_bin, tipo='open', kernel_size=5):
        ope = {
            1: cv2.MORPH_OPEN,
            2: cv2.MORPH_CLOSE,
            3: cv2.MORPH_DILATE,
            4: cv2.MORPH_ERODE
        }
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(imagen_bin, ope.get(tipo), kernel)

    def anotar_imagen(self, imagen, texto, forma='rect', pos=(50, 50), tamaño=50):
        anotada = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)
        if forma == 1:
            cv2.rectangle(anotada, pos, (pos[0] + tamaño, pos[1] + tamaño), (255, 0, 0), 2)
        elif forma == 2:
            cv2.circle(anotada, pos, tamaño, (0, 255, 0), 2)
        cv2.putText(anotada, texto, (pos[0], pos[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        return anotada


d = DICOMC("datosDICOM")
im = d.cargar_dicom_y_reconstruir()
n, e, i = d.obt_info()
p = Paciente(n, e, i, im)
# im = p.getImagen()
d.traslacion(1)
