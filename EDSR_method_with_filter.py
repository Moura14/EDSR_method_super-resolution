import cv2
import numpy as np

def preprocess_image(image):
    # Aplicar filtro para aumentar a nítidez
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0,-1,0]])
    denoised_image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    return denoised_image

def combine_images_superresolution(images, upscale_factor=4, sr_model=None):
    # Verificar se há pelo menos 2 imagens de baixa resolução
    if len(images) < 2:
        raise ValueError("Pelo menos duas imagens são necessárias para super-resolução combinada.")

    # Aplicar o modelo de super-resolução em cada imagem de baixa resolução
    sr_images = [sr_model.upsample(preprocess_image(img)) for img in images]

    # Somar as imagens de super-resolução
    superres_image = np.sum(sr_images, axis=0)

    # Normalizar a imagem resultante (dividir pela quantidade de imagens para evitar valores muito altos)
    superres_image = superres_image / len(images)

    # Converter a imagem para o formato de 8 bits por canal
    superres_image = cv2.convertScaleAbs(superres_image)

    # Aplicar o filtro bilateral para redução de ruídos
    superres_image = cv2.bilateralFilter(superres_image, d=9, sigmaColor=75, sigmaSpace=75)

    # Converter a imagem de alta resolução de volta para o formato BGR
    superres_image = superres_image.astype(np.uint8)

    return superres_image

# Carregar imagens de baixa-resolução
images = []
for i in range(1, 5):  # Substitua '1' e '5' pelos índices das imagens de baixa resolução desejadas
    img_path = f'images/frame_{i}.tif'
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"A leitura da imagem {i} falhou. Verifique o caminho para o arquivo de imagem.")
    images.append(img)

# Inicializar o modelo de Super-Resolução
sr = cv2.dnn_superres.DnnSuperResImpl_create()
path = 'model/EDSR_x4.pb'
sr.readModel(path)
sr.setModel('edsr', 4)

# Realizar a super-resolução combinada usando o modelo EDSR_x4 com 5 imagens
superres_image = combine_images_superresolution(images, upscale_factor=4, sr_model=sr)

cv2.imwrite('output/imagem_super_resolvida.jpg', superres_image)

# Exibir a imagem de super-resolução combinada em uma janela
cv2.imshow('Super-Resolution Combined', superres_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
