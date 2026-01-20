def infer_location(image_metadata):
    """
    Infer geospatial exposure from image EXIF metadata.
    This function is conservative and OSINT-safe.
    """

    if not image_metadata:
        return None

    # Common GPS keys from EXIF
    gps_keys = [
        "GPSLatitude",
        "GPSLongitude",
        "GPS GPSLatitude",
        "GPS GPSLongitude"
    ]

    for key in gps_keys:
        if key in image_metadata:
            return {
                "risk": 15,
                "evidence": "Geolocation data detected in image metadata (EXIF GPS coordinates)"
            }

    return None