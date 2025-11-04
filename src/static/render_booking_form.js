document.addEventListener("DOMContentLoaded", () => {
  const formData = JSON.parse(
    document.getElementById("form-data").textContent
  );

  const specialties = document.getElementById("specialties");
  const doctors = document.getElementById("doctors");
  const services = document.getElementById("services");
  const appointment_date = document.getElementById("appointment_date");
  const appointment_time = document.getElementById("appointment_time");

  doctors.innerHTML = "<option value=''>Select doctor</option>";
  doctors.disabled = true;
  services.innerHTML = "<option value=''>Select service</option>";
  services.disabled = true;
  appointment_date.innerHTML = "<option value=''>Select appointment date</option>";
  appointment_date.disabled = true;
  appointment_time.innerHTML = "<option value=''>Select appointment time</option>";
  appointment_time.disabled = true;

  Object.values(formData).forEach((specialty) => {
    specialties.add(new Option(specialty.title, specialty.id));
  })

  specialties.addEventListener("change", () => {
    const specialty = specialties.value;

    doctors.innerHTML = "<option value=''>Select doctor</option>";
    doctors.disabled = !specialty;

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

  services.addEventListener("change", () => {
    const specialty = specialties.value;
    const doctor = doctors.value;

    appointment_date.innerHTML = "<option value=''>Select appointment date</option>";
    appointment_date.disabled = !doctor;
    appointment_time.innerHTML = "<option value=''>Select appointment time</option>";
    appointment_time.disabled = true;

    const doctorsArr = formData[specialty - 1].doctors;
    for (const doctorsElem of doctorsArr) {
      if (doctor == doctorsElem.id) {
        Object.keys(doctorsElem.schedule).forEach((date) => {
          appointment_date.add(new Option(date, date));
        });
      }
    }
  });

  appointment_date.addEventListener("change", () => {
    const specialty = specialties.value;
    const doctor = doctors.value;
    const date = appointment_date.value;

    appointment_time.innerHTML = "<option value=''>Select appointment time</option>";
    appointment_time.disabled = !appointment_date;

    const doctorsArr = formData[specialty - 1].doctors;
    for (const doctorsElem of doctorsArr) {
      if (doctor == doctorsElem.id) {
        Object.values(doctorsElem.schedule[date]).forEach((time) => {
          appointment_time.add(new Option(time, time));
        });
      }
    }
  });
});
