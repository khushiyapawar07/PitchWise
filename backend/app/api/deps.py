from app.services.data_loader import ProcessedDataStore, get_data_store


def data_store() -> ProcessedDataStore:
    return get_data_store()
