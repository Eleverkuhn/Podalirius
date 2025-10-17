from fastapi.templating import Jinja2Templates

from config import Config


class BaseRouter:
    template = Jinja2Templates(directory=Config.templates_dir)


class Prefixes:
    AUTH = "/auth"
    MY = "/my"
