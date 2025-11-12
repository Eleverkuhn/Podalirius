import pytest

from data.sql_models import Doctor
from data.service_data import ServiceDataConverter


class TestServiceDataConstructor:
    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test_convert_to_outer(self, doctor: Doctor) -> None:
        converter = ServiceDataConverter(doctor, doctor.services[0])
        service_outer = converter.convert_to_outer()
        assert service_outer.price == 3000
