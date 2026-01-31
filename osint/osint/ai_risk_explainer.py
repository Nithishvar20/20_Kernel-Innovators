def explain_risk(features, feature_names):
    explanations = []

    for value, name in zip(features[0], feature_names):
        if name == "platform_count" and value > 3:
            explanations.append("Username appears on many platforms")
        if name == "username_reuse" and value == 1:
            explanations.append("Same username reused across platforms")
        if name == "image_metadata" and value == 1:
            explanations.append("Images contain metadata")
        if name == "gps_metadata" and value == 1:
            explanations.append("Location data exposed in media")
        if name == "exposed_files" and value > 0:
            explanations.append("Sensitive website files publicly accessible")

    return explanations