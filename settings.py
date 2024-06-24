import os
from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    name: str = str(os.environ.get("APP_NAME", "PDF2MD"))
    contact_name: str = str(os.environ.get("ADMIN_NAME", "Thomas Hanke"))
    admin_email: str = str(os.environ.get("ADMIN_MAIL", "thomas.hanke82@gmail.com"))
    items_per_user: int = 50
    version: str = str(os.environ.get("APP_VERSION")) or "v0.0.2"
    config_name: str = str(os.environ.get("APP_MODE")) or "development"
    openapi_url: str = "/api/openapi.json"
    docs_url: str = "/api/docs"
    source: str = str(os.environ.get("APP_SOURCE", "https://github.com/ThHanke/PDF2MD"))
    desc: str = str(os.environ.get("APP_DESC", ""))
    org_site: str = str(os.environ.get("ORG_SITE", "https://github.com/ThHanke"))
