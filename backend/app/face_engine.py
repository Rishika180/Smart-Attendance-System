"""
Face detection + recognition engine.

Detection:  MTCNN (facenet-pytorch)
Recognition: FaceNet embeddings (InceptionResnetV1, pretrained on VGGFace2)

Both models are loaded ONCE as module-level singletons when this file is
first imported, so a request never pays model-loading cost.

Recognition works by comparing the 512-d embedding of a detected face
against the stored average embedding of every registered student, using
Euclidean distance. A match is accepted only if the closest student is
within RECOGNITION_THRESHOLD.
"""
import json
from io import BytesIO

import numpy as np
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Lower = stricter match. 0.9 is the commonly recommended cutoff for
# VGGFace2-trained FaceNet embeddings (L2 distance in embedding space).
RECOGNITION_THRESHOLD = 0.9

# --- Model singletons -------------------------------------------------
# keep_all=False -> registration: only the single largest/most confident
# face in the frame is used (a student photographing themselves).
_mtcnn_single = MTCNN(keep_all=False, device=DEVICE)

# keep_all=True -> attendance marking: a classroom frame may contain
# several students at once, so every detected face is returned.
_mtcnn_multi = MTCNN(keep_all=True, device=DEVICE)

_resnet = InceptionResnetV1(pretrained="vggface2", device=DEVICE).eval()


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """Decode raw image bytes (as received over HTTP) into a PIL image."""
    return Image.open(BytesIO(image_bytes)).convert("RGB")


def embedding_to_json(embedding: np.ndarray) -> str:
    return json.dumps(embedding.tolist())


def json_to_embedding(text: str) -> np.ndarray:
    return np.array(json.loads(text), dtype=np.float32)


def get_single_embedding(image: Image.Image) -> np.ndarray | None:
    """
    Used during student registration.

    Detects the single most prominent face in `image`, aligns and crops
    it, and returns its 512-d FaceNet embedding. Returns None if no face
    was detected.
    """
    with torch.no_grad():
        face_tensor = _mtcnn_single(image)
        if face_tensor is None:
            return None
        embedding = _resnet(face_tensor.unsqueeze(0).to(DEVICE))
        return embedding.detach().cpu().numpy()[0]


def detect_and_embed_all(image: Image.Image):
    """
    Used during attendance marking.

    Detects every face in `image` and returns a list of
    (box, embedding) tuples, where box = [x1, y1, x2, y2] in pixel
    coordinates. Returns an empty list if no faces were detected.
    """
    with torch.no_grad():
        face_tensors = _mtcnn_multi(image)
        if face_tensors is None:
            return []

        # .detect() re-runs the P/R/O-net cascade, but is the only way
        # facenet-pytorch exposes pixel-coordinate boxes; order matches
        # the face_tensors returned above since both come from the same
        # detector on the same (unmodified) image.
        boxes, _ = _mtcnn_multi.detect(image)
        if boxes is None:
            return []

        embeddings = _resnet(face_tensors.to(DEVICE)).detach().cpu().numpy()

        results = []
        for box, embedding in zip(boxes, embeddings):
            x1, y1, x2, y2 = [int(round(v)) for v in box]
            results.append(([x1, y1, x2, y2], embedding))
        return results


def find_best_match(embedding: np.ndarray, known_students: list[dict]):
    """
    known_students: list of {"id", "name", "roll_no", "class_name",
    "embedding": np.ndarray}

    Returns (student_dict, distance) for the closest match, or
    (None, None) if no registered student is within
    RECOGNITION_THRESHOLD.
    """
    if not known_students:
        return None, None

    best_student = None
    best_distance = float("inf")

    for student in known_students:
        distance = float(np.linalg.norm(embedding - student["embedding"]))
        if distance < best_distance:
            best_distance = distance
            best_student = student

    if best_distance <= RECOGNITION_THRESHOLD:
        return best_student, best_distance
    return None, best_distance
