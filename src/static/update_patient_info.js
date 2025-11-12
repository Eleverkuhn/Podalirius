document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("patient-container")
  const url = container.dataset.apiUrl
  document.getElementById("update-patient-form").addEventListener("submit", async (e) => {
    e.preventDefault()
    const form = e.target;
    const formData = new FormData(e.target);

    const response = await fetch(url, {
      method: "PUT",
      body: new FormData(form)
    });
     if (response.status === 422) {
       const html = await response.text();
       const parser = new DOMParser();
       const doc = parser.parseFromString(html, "text/html")

       const newForm = doc.getElementById("update-patient-form");
       const currentForm = document.getElementById("update-patient-form");
       if (newForm && currentForm) {
         currentForm.replaceWith(newForm);
       }
     } 
  })
})
