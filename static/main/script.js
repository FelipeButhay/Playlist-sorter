// Función que actualiza el span correspondiente
function setupFileInput(inputId, spanId) {
    const input = document.getElementById(inputId);
    const span = document.getElementById(spanId);

    if (!input || !span) return;

    input.addEventListener("change", function() {
        if (input.files && input.files.length > 0) {
            span.textContent = input.files[0].name;
        } else {
            span.textContent = "No file selected";
        }
    });
}

// Configuramos todos los inputs de archivos
setupFileInput("backup-file", "backup-filename");

const typeSelector = document.querySelector(".type-selector");
playlist_selected = true;

const playlist_input_div = document.querySelector(".data-container .playlist-input");
const playlist_input     = document.querySelector(".data-container .playlist-input input");
const backup_input_div   = document.querySelector(".data-container .backup-input");
const backup_input       = document.querySelector(".data-container .backup-input input");

function toggleInputs() {
    playlist_input_div.classList.toggle("hidden");
    backup_input_div.classList.toggle("hidden");

    playlist_input.required = !playlist_input_div.classList.contains("hidden");
    backup_input.required = !backup_input_div.classList.contains("hidden");
}

typeSelector.addEventListener("click", () => {
    playlist_selected = !playlist_selected;

    const selected = document.querySelector('.type-selector .types[data-selected= "true"]');
    const not_selected = document.querySelector('.type-selector .types[data-selected="false"]');

    selected.dataset.selected = "false";
    not_selected.dataset.selected = "true";

    document.querySelector(".type-selector .selector").style.left = playlist_selected ? "0" : "50%";

    toggleInputs();
});