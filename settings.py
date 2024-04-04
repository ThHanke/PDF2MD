import os
#from pydantic import BaseSettings
from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    name: str = str(os.environ.get("APP_NAME","BaseFastApiApp"))
    contact_name: str = str(os.environ.get("ADMIN_NAME","Max Mustermann"))
    admin_email: str = str(os.environ.get("ADMIN_MAIL","app_admin@example.com"))
    items_per_user: int = 50
    version: str = str(os.environ.get("APP_VERSION")) or "v1.0.0"
    config_name: str = str(os.environ.get("APP_MODE")) or "development"
    openapi_url: str ="/api/openapi.json"
    docs_url: str = "/api/docs"
    source: str = str(os.environ.get("APP_SOURCE","https://example.com"))
    desc: str = str(os.environ.get("APP_DESC",""))
    org_site: str = str(os.environ.get("ORG_SITE","https://example.com"))
