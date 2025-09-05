from fastapi import APIRouter

router = APIRouter()


@router.get("/", name="main")
def index() -> None:
    pass
