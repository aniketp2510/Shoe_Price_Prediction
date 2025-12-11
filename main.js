// Button Loader + Input Validation + Shake effect
const form = document.getElementById("predictionForm");
const predictBtn = document.getElementById("predictBtn");
const btnText = document.querySelector(".btn-text");
const loader = document.querySelector(".loader");

form.addEventListener("submit", function (e) {
    const fields = form.querySelectorAll("input,select");

    let valid = true;
    fields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add("shake");
            valid = false;
            setTimeout(() => field.classList.remove("shake"), 500);
        }
    });

    if (!valid) {
        e.preventDefault();
        return;
    }

    btnText.style.display = "none";
    loader.style.display = "inline-block";
});

// Dark / Light Mode Toggle
function toggleTheme() {
    document.body.classList.toggle("dark");
}
