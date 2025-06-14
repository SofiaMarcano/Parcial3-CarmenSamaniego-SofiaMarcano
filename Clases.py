import pydicom
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
import random
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
        archivos = sorted([
            os.path.join(self.carpeta, f) for f in os.listdir(self.carpeta)
            if f.lower().endswith('.dcm')
        ])
        if not archivos:
            print("❌ No se encontraron archivos DICOM en la carpeta.")
            return None

        # Leer todos los archivos con metadata
        slices = []
        for f in archivos:
            ds = pydicom.dcmread(f)
            if hasattr(ds, 'ImagePositionPatient'):
                z = float(ds.ImagePositionPatient[2])
            elif hasattr(ds, 'SliceLocation'):
                z = float(ds.SliceLocation)
            else:
                print(f"⚠️ Archivo sin coordenada Z: {f}")
                continue
            slices.append((z, ds))

        # Ordenar por coordenada Z
        slices.sort(key=lambda x: x[0])
        imagenes = [ds.pixel_array for (_, ds) in slices]

        if not imagenes:
            print("❌ No se pudieron leer imágenes válidas.")
            return None

        self.meta_info = slices[0][1]
        self.volumen = np.stack(imagenes, axis=0)
        return self.volumen

    def see_cortes(self):
        medio_z = self.volumen.shape[0] // 2
        medio_y = self.volumen.shape[1] // 2
        medio_x = self.volumen.shape[2] // 2

        corte_transversal = self.volumen[medio_z, :, :]
        corte_coronal = self.volumen[:, medio_y, :]
        corte_sagital = self.volumen[:, :, medio_x]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(corte_transversal, cmap='gray')
        axes[0].set_title("Corte Transversal")
        axes[0].axis('off')

        axes[1].imshow(corte_coronal, cmap='gray', aspect='auto')
        axes[1].set_title("Corte Coronal")
        axes[1].axis('off')

        axes[2].imshow(corte_sagital, cmap='gray', aspect='auto')
        axes[2].set_title("Corte Sagital")
        axes[2].axis('off')

        plt.tight_layout()
        ruta_salida = os.path.join(os.getcwd(), self.carpeta)
        plt.savefig(ruta_salida, dpi=300)
        print(f"Imagen guardada en: {ruta_salida}")
        plt.show()

    def obt_info(self):
        if self.meta_info:
            nombre = self.meta_info.get('PatientName', 'Desconocido')
            edad = self.meta_info.get('PatientAge', '00Y')
            id_paciente = self.meta_info.get('PatientID', '0000')
            return str(nombre), int(edad[:-1]), str(id_paciente)
        return "Anonimo", 0, "0000"
    
    def traslacion(self, valor,c):
        if valor == "1":
            tx = 300
            ty = 0
        elif valor == "2":
            tx = -300
            ty = 0
        elif valor == "3":
            tx = 300
            ty = 300
        elif valor == "4":
            tx = 0
            ty = 400
        else:
            tx = 0
            ty = 0
            print("No eligió bien, no se traslada")
        try:
            # corte= pydicom.dcmread(f"datosDICOM/{c}")
            # imagen = c.pixel_array
            imagen = c[20,:,:]
            print("Corte 20 transversal")
            MT = np.float32([[1, 0, tx], [0, 1, ty]])
            row,col= imagen.shape
            #Traslación
            tras = cv2.warpAffine(imagen,MT,(col,row))

            plt.figure(figsize=(15,8))
            plt.subplot(1,2,1)
            plt.imshow(imagen, cmap=plt.cm.bone)
            plt.title('Original')
            plt.subplot(1,2,2)
            plt.imshow(tras, cmap=plt.cm.bone)
            plt.title('Trasladada')
            plt.show() 
            tras_guardar = cv2.normalize(tras, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            numero = random.randint(100, 999)
            cv2.imwrite(f"datosDICOM/corte_trasladado_{numero}.png",tras_guardar)
            plt.close()
        except:
            print("No eligió un corte valido")
        
        
class ImagenM:
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
        tipo_cv = tipos.get(tipo, cv2.THRESH_BINARY)
        gris = cv2.cvtColor(self.imagen, cv2.COLOR_BGR2GRAY)
        _, binarizada = cv2.threshold(gris, umbral, max_val, tipo_cv)
        # Normalización opcional para visualización
        return cv2.normalize(binarizada, None, 0, 255, cv2.NORM_MINMAX)

    def trans_morfo(self, imagen_bin, tipo='open', kernel_size=5):
        ope = {
            1: cv2.MORPH_OPEN,
            2: cv2.MORPH_CLOSE,
            3: cv2.MORPH_DILATE,
            4: cv2.MORPH_ERODE,
        }
        operacion = ope.get(tipo, cv2.MORPH_OPEN)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        procesada = cv2.morphologyEx(imagen_bin, operacion, kernel)
        return cv2.normalize(procesada, None, 0, 255, cv2.NORM_MINMAX)

    def anotar_imagen(self, imagen, texto, forma=1):
        if len(imagen.shape) == 2:
            anotada = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)
        else:
            anotada = imagen.copy()

        alto, ancho = anotada.shape[:2]
        tamaño = min(alto, ancho) // 5
        x = ancho // 20
        y = alto // 10

        color_figura = (0, 255, 0) if forma == 2 else (255, 0, 0)
        color_texto = (0, 255, 255)
        grosor = 2

        if forma == 1:
            cv2.rectangle(anotada, (x, y), (x + tamaño, y + tamaño), color_figura, grosor)
            pos_texto = (x + 10, y + tamaño // 2)
        elif forma == 2:
            centro = (x + tamaño // 2, y + tamaño // 2)
            cv2.circle(anotada, centro, tamaño // 2, color_figura, grosor)
            pos_texto = (x + 10, y + tamaño // 2)

        for i, linea in enumerate(texto.split("\n")):
            cv2.putText(anotada, linea,
                        (pos_texto[0], pos_texto[1] + i * 22),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color_texto,
                        2,
                        cv2.LINE_AA)
        return anotada


