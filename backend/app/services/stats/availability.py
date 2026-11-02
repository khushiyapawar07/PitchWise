from app.models.schemas import Availability

LIMITED_THRESHOLD = 3


def availability_from_sample(sample_size: int, required: int = 1) -> Availability:
    if sample_size < required:
        return "unavailable"
    if sample_size < LIMITED_THRESHOLD:
        return "limited"
    return "sufficient"
