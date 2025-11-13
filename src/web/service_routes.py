from fastapi import APIRouter, status, Depends, Request
from fastapi_utils.cbv import cbv
from starlette.templating import _TemplateResponse

from service.service_services import ServicePage, get_service_page
from web.base_routes import BaseRouter

router = APIRouter(prefix="/services")


@cbv(router)
class Service(BaseRouter):
    @router.get("/lab-tests", name="lab_tests", status_code=status.HTTP_200_OK)
    def get_lab_tests(
            self,
            request: Request,
            service_page: ServicePage = Depends(get_service_page)
    ) -> _TemplateResponse:
        lab_tests = service_page.get_lab_tests()
        content = {"request": request, "lab_tests": lab_tests}
        response = self.template.TemplateResponse(
            "lab_tests.html", content
        )
        return response
