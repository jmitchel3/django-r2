import pathlib
from functools import lru_cache

from django.apps import apps
from django.conf import settings

from django_r2.helpers.staticfiles.locators import locate_app_static_files


@lru_cache
def get_app_path():
    """Get the path to the django_r2 app directory"""
    return pathlib.Path(apps.get_app_config("django_r2").path)


@lru_cache
def django_r2_css_paths(*args, **kwargs) -> list[str]:
    app_path = get_app_path()
    static_dir = app_path / "staticfiles"
    django_r2_dir = static_dir / "django_r2"
    theme_dir = django_r2_dir / "theme"
    theme_prod = theme_dir / "prod"
    theme_dev = theme_dir / "dev"

    if settings.DEBUG and theme_dev.exists():
        css_files = [str(x.relative_to(static_dir)) for x in theme_dev.glob("**/*.css")]
        return css_files
    if not theme_prod.exists():
        return []
    css_files = [str(x.relative_to(static_dir)) for x in theme_prod.glob("**/*.css")]
    return css_files


@lru_cache
def django_r2_js_paths(*args, **kwargs) -> list[str]:
    """
    Return paths to upload-related JS files from either dev or prod directories
    """
    app_path = get_app_path()
    static_dir = app_path / "static" / "django_r2" / "js"
    dev_dir = static_dir / "dev"
    prod_dir = static_dir / "prod"

    if settings.DEBUG and dev_dir.exists():
        js_files = [f"django_r2/js/dev/{x.name}" for x in dev_dir.glob("upload*.js")]
        return js_files
    if not prod_dir.exists():
        return []
    js_files = [f"django_r2/js/prod/{x.name}" for x in prod_dir.glob("upload*.js")]
    return js_files


@lru_cache
def django_r2_static_files(*args, **kwargs):
    """
    Return a list of static files for django_r2
    """
    django_r2_css_files = locate_app_static_files(
        "django_r2", "*.css", parent_dir_name="prod"
    )
    django_r2_upload_js_files = locate_app_static_files(
        "django_r2", "upload*.js", parent_dir_name="prod"
    )
    print(django_r2_css_files)
    print(django_r2_upload_js_files)
    return {
        "django_r2_css_files": django_r2_css_files,
        "django_r2_upload_js_files": django_r2_upload_js_files,
    }
