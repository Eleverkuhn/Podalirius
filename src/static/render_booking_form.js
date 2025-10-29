document.addEventListener("DOMContentLoaded", () => {
  const formData = JSON.parse(
    document.getElementById("form-data").textContent
  );

  const specialties = document.getElementById("specialties");
  const doctors = document.getElementById("doctors");
  const services = document.getElementById("services");

  doctors.innerHTML = "<option value=''>Select doctor</option>";
  doctors.disabled = true;
  services.innerHTML = "<option value=''>Select service</option";
  services.disabled = true;

  Object.values(formData).forEach((specialty) => {
    specialties.add(new Option(specialty.title, specialty.id));
  })

  specialties.addEventListener("change", () => {
    const specialty = specialties.value;

    doctors.innerHTML = "<option value=''>Select doctor</option>";
    doctors.disabled = !specialty;
    services.innerHTML = "<option value=''>Select service</option";
    services.disabled = true;

    const specialtyArr = formData[specialty - 1];
    for (const specialtyElem of formData) {
      if (specialty == specialtyElem.id) {
        Object.values(specialtyArr.doctors).forEach((doctor) => {
          doctors.add(new Option(doctor.full_name, doctor.id));
        });
      }
    }
  });

  doctors.addEventListener("change", () => {
    const specialty = specialties.value;
    const doctor = doctors.value;

    services.innerHTML = "<option value=''>Select service</option>";
    services.disabled = !doctor;

    const doctorsArr = formData[specialty - 1].doctors;
    for (const doctorsElem of doctorsArr) {
      if (doctor == doctorsElem.id) {
        Object.values(doctorsElem.services).forEach((service) => {
          services.add(new Option(`${service.title}: ${service.price}`, service.id));
        });
      }
    }
  });
});
