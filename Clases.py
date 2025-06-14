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
    def getImagen(self):
        return self.imagen_3d
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
    def traslacion(self,imagen, valor):
        print(im.shape)
        if valor == "1":
            tx = 30
            ty = 0
        elif valor == "2":
            tx = -30
            ty = 0
        elif valor == "3":
            tx = 50
            ty = 50
        elif valor == "4":
            tx = 0
            ty = 40
            
        MT = np.float32([[1, 0, tx], [0, 1, ty]])
        row, col, chn=np.shape(imagen)
        #Traslación
        tras = cv2.warpAffine(imagen,MT,(col,row))
        plt.imshow(tras)
        plt.axis('off')
        print("ya")
            
            # print("\nValores de traslación predefinidos:")
            # print("1. Traslación derecha (30, 0)")
            # print("2. Traslación izquierda (-30, 0)")
            # print("3. Traslación diagonal (50, 50)")
            # print("4. Traslación vertical (0, 40)")

d = DICOMC("datosDICOM")
d.cargar_dicom_y_reconstruir()
d.obt_info()
im = d.getImagen()
d.traslacion(im,1)
