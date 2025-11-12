from fastapi import APIRouter, status, Request, Depends
from fastapi_utils.cbv import cbv
from starlette.templating import _TemplateResponse

from service.specialty_services import SpecialtyPage, get_specialty_page
from web.base_routes import BaseRouter

router = APIRouter(prefix="/specialties")


@cbv(router)
class Specialty(BaseRouter):
    @router.get("/", name="all", status_code=status.HTTP_200_OK)
    def get_all(
            self,
            request: Request,
            specialty_page: SpecialtyPage = Depends(get_specialty_page)
    ) -> _TemplateResponse:
        specialties = specialty_page.get_all_specialties()
        content = {"request": request, "specialties": specialties}
        response = self.template.TemplateResponse("specialties.html", content)
        return response

    @router.get("/{title}", name="specialty", status_code=status.HTTP_200_OK)
    def get(
            self,
            request: Request,
            title: str,
            specialty_page: SpecialtyPage = Depends(get_specialty_page),
    ) -> _TemplateResponse:
        specialty = specialty_page.get_detailed_info(title)
        content = {"request": request, "specialty": specialty}
        response = self.template.TemplateResponse(
            "specialty_detail.html", content
        )
        return response
