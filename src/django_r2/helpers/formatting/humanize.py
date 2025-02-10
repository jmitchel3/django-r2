def humanize_filesize(size_in_bytes: int) -> str:
    """
    Convert a file size in bytes to a human-readable string.

    Args:
        size_in_bytes: File size in bytes

    Returns:
        str: Human-readable file size (e.g., "1.5 MB", "2.3 GB")
    """
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_in_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    # Round to 2 decimal places if size is not in bytes
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"
