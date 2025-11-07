document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("update");
  const itemId = button.dataset.appointmentId;

  button.addEventListener("click", () => {
    fetch(`/my/appointments/${itemId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: "cancelled"
      })
    })
      .then(response => {
        if (response.redirected) {
          window.location.href = response.url;
        } else {
          window.location.reload()
        }
      })
      .catch(console.error);
  });
});
