from pathlib import Path
from typing import List, Optional

from django.apps import apps
from django.contrib.staticfiles.finders import get_finders


def locate_app_static_files(
    app_name: str,
    file_pattern: str = "*",
    recursive: bool = True,
    parent_dir_name: Optional[str] = None,
) -> List[Path]:
    """
    Find static files for a specific Django installed app and return their relative paths
    suitable for use with Django's {% static %} template tag.

    Args:
        app_name (str): Name of the installed app (e.g., 'django.contrib.admin')
        file_pattern (str): Pattern to match files (e.g., '*.js', '*.css'). Defaults to all files.
        recursive (bool): Whether to search subdirectories. Defaults to True.
        parent_dir_name (Optional[str]): Filter files by parent directory name (e.g., 'prod', 'dev').
            If None, includes files from all parent directories.

    Returns:
        List[Path]: List of relative paths to static files, suitable for {% static %} template tag

    Raises:
        LookupError: If the app is not found in INSTALLED_APPS
        AppRegistryNotReady: If Django apps aren't loaded yet

    Example:
        # Find all JS files in the 'prod' directory of myapp
        prod_js_files = locate_app_static_files('myapp', '*.js', parent_dir_name='prod')
        # Result: ['myapp/prod/script.js', 'myapp/prod/utils.js']

        # Use in template:
        # {% static path %} where path is from the returned list
    """
    # Check if the app is installed
    try:
        app_config = apps.get_app_config(app_name.split(".")[-1])
    except LookupError:
        raise LookupError(f"App '{app_name}' not found in INSTALLED_APPS")

    static_files = []

    # Get all static file finders
    for finder in get_finders():
        # Check if the finder can list files (like FileSystemFinder and AppDirectoriesFinder)
        if hasattr(finder, "list"):
            for path, storage in finder.list([]):
                # Get the full path of the static file
                full_path = Path(storage.path(path))

                # Get the relative path that works with {% static %}
                relative_path = Path(path)

                # Check if this file belongs to our target app
                if app_config.path in str(full_path):
                    # Apply parent directory filter if specified
                    if (
                        parent_dir_name is not None
                        and full_path.parent.name != parent_dir_name
                    ):
                        continue

                    # Apply pattern matching and recursive filtering
                    if recursive:
                        if full_path.match(file_pattern):
                            static_files.append(relative_path)
                    else:
                        # For non-recursive, only match files in the immediate directory
                        if full_path.parent == Path(
                            app_config.path
                        ) / "static" and full_path.match(file_pattern):
                            static_files.append(relative_path)

    return sorted(static_files)
