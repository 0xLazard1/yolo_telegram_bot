from PIL import Image, ImageDraw, ImageFont
import io
from typing import Tuple, Dict
from ultralytics import YOLO


class ImageProcessor:
    """Classe responsable de la détection de personnes avec YOLO"""

    def __init__(self):
        """Initialise le modèle YOLO"""
        self.model = YOLO('yolov8n.pt')

    def bytes_to_image(self, image_bytes: bytes) -> Image.Image:
        """Convertit des bytes en image PIL"""
        return Image.open(io.BytesIO(image_bytes))

    def image_to_bytes(self, image: Image.Image, format: str = "PNG") -> bytes:
        """Convertit une image PIL en bytes"""
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()

    def detect_persons(self, image: Image.Image) -> Tuple[int, list, list]:
        """
        Détecte les personnes dans une image

        Returns:
            Tuple[int, list, list]: Nombre de personnes, boîtes englobantes, scores de confiance
        """
        # Exécute la détection
        results = self.model(image, verbose=False)

        # Filtre uniquement la classe "person" (classe 0 dans COCO)
        boxes = []
        confidences = []

        for result in results:
            for box in result.boxes:
                # Vérifie si c'est une personne (classe 0)
                if int(box.cls[0]) == 0:
                    boxes.append(box.xyxy[0].cpu().numpy())
                    confidences.append(float(box.conf[0]))

        return len(boxes), boxes, confidences

    def draw_detections(self, image: Image.Image, boxes: list, confidences: list) -> Image.Image:
        """Dessine les boîtes de détection sur l'image"""
        draw = ImageDraw.Draw(image)

        # Essaie de charger une police, sinon utilise la police par défaut
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()

        for i, (box, conf) in enumerate(zip(boxes, confidences)):
            x1, y1, x2, y2 = box

            # Dessine le rectangle
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

            # Dessine le label
            label = f"Personne {i+1}: {conf:.2%}"

            # Dessine un fond pour le texte
            bbox = draw.textbbox((x1, y1 - 25), label, font=font)
            draw.rectangle(bbox, fill="red")
            draw.text((x1, y1 - 25), label, fill="white", font=font)

        return image

    def process_image(self, image_bytes: bytes) -> Tuple[bytes, str, Dict]:
        """
        Pipeline complet de détection de personnes

        Args:
            image_bytes: Image en bytes

        Returns:
            Tuple[bytes, str, Dict]: Image annotée, message de description, statistiques
        """
        # Conversion
        image = self.bytes_to_image(image_bytes)

        # Détection des personnes
        person_count, boxes, confidences = self.detect_persons(image)

        # Dessine les détections sur l'image
        annotated_image = self.draw_detections(image.copy(), boxes, confidences)

        # Crée le message
        if person_count == 0:
            message = "Aucune personne détectée"
        elif person_count == 1:
            message = f"1 personne détectée (confiance: {confidences[0]:.1%})"
        else:
            avg_conf = sum(confidences) / len(confidences)
            message = f"{person_count} personnes détectées (confiance moyenne: {avg_conf:.1%})"

        # Statistiques
        stats = {
            "count": person_count,
            "confidences": confidences,
            "boxes": boxes
        }

        # Conversion en bytes
        result_bytes = self.image_to_bytes(annotated_image)

        return result_bytes, message, stats
