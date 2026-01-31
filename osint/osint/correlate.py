def correlate_data(platforms, image_data):
    result = {
        "platforms_found": platforms,
        "image_metadata": image_data,
        "signals": {}
    }
    if image_data:
        result["signals"]["geo"] = "HIGH" if "GPSLatitude" in image_data else "LOW"

    return result