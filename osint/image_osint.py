from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _convert_to_degrees(value):
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1]
    s = value[2][0] / value[2][1]
    return d + (m / 60.0) + (s / 3600.0)


def extract_image_metadata(image_path):
    metadata = {}

    try:
        img = Image.open(image_path)
        exif_data = img._getexif()

        if not exif_data:
            return metadata

        gps_data = {}

        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)

            # -------- GPS --------
            if decoded == "GPSInfo":
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[sub_decoded] = value[gps_tag]

            # -------- HIGH-VALUE OSINT TAGS --------
            elif decoded in [
                "Make",
                "Model",
                "Software",
                "DateTimeOriginal",
                "DateTime",
                "ExposureTime",
                "FNumber",
                "ISOSpeedRatings",
                "FocalLength"
            ]:
                metadata[decoded] = str(value)

        # -------- GPS CONVERSION --------
        if (
            "GPSLatitude" in gps_data and
            "GPSLongitude" in gps_data and
            "GPSLatitudeRef" in gps_data and
            "GPSLongitudeRef" in gps_data
        ):
            lat = _convert_to_degrees(gps_data["GPSLatitude"])
            lon = _convert_to_degrees(gps_data["GPSLongitude"])

            if gps_data["GPSLatitudeRef"] != "N":
                lat = -lat
            if gps_data["GPSLongitudeRef"] != "E":
                lon = -lon

            metadata["gps"] = {
                "lat": round(lat, 6),
                "lon": round(lon, 6)
            }

    except Exception:
        pass  # OSINT-safe

    return metadata