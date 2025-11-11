document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("appointment-container")
  const url = container.dataset.apiUrl

  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Data:', data);
      const appointment_date = document.getElementById("appointment_date");
      const appointment_time = document.getElementById("appointment_time");
      appointment_time.innerHTML = "<option value=''>Select appointment date</option>"
      appointment_time.disabled = true;

      Object.keys(data).forEach((date) => {
        appointment_date.add(new Option(date, date))
      });

      appointment_date.addEventListener("change", () => {
        const date = appointment_date.value;
        appointment_time.innerHTML = "<option value=''>Select appointment date</option>"
        appointment_time.disabled = !appointment_date;

        Object.values(data[date]).forEach((time) => {
          appointment_time.add(new Option(time, time));
        });
      });

      document.getElementById("reschedule-form").addEventListener("submit", async (e) => {
        e.preventDefault()
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        const appointmentUrl = container.dataset.appointmentUrl

        const response = await fetch(appointmentUrl, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
        });

        if (response.redirected) {
          window.location.href = response.url
        } else {
          window.location.reload()
        }
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
})
