// ---------------------------
//          VOLUMEN
// ---------------------------

const slider = document.getElementById("volume-range");
const icon = document.getElementById("volume-icon").querySelector("use");

function updateVolume() {
    const value = slider.value;
    slider.style.background = `linear-gradient(to right, #1ED760 0%, #1ED760 ${value}%, #aaa ${value}%, #aaa 100%)`;

    if (value == 0) {
        icon.setAttribute("href", "#icon-volume-none");
    } else if (value <= 50) {
        icon.setAttribute("href", "#icon-volume-low");
    } else {
        icon.setAttribute("href", "#icon-volume-high");
    }
}

// Inicializamos
updateVolume();

// Actualizamos al mover
slider.addEventListener("input", function() {
    updateVolume();
});

// ---------------------------------
//       HOVERS COMO LA GENTE
// ---------------------------------

const spans = document.querySelectorAll(".song-data span")

spans.forEach(span => {
    const style = window.getComputedStyle(span);
    span.dataset.originalFontSize = parseFloat(style.fontSize);
});

const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");

function measureText(texto, fontSize, fontFamily) {
  ctx.font = `${fontSize} ${fontFamily}`;
  return ctx.measureText(texto).width;
}

function fixText() {
    const container = document.querySelector(".song-data");
    const containerStyle = getComputedStyle(container);
    const containerWidth = parseFloat(containerStyle.width);
  
    let n = 0;

    spans.forEach(span => {
        const style = window.getComputedStyle(span);
        const fontFamily = style.fontFamily;
        let fontSize = parseFloat(span.dataset.originalFontSize);
        let texto = span.dataset.fullText;
        
        for (let i = 0; i < 3; i++) {
            let newFontSize = fontSize * (1 - i / 4);
            let textWidth = measureText(texto, newFontSize + "px", fontFamily);

            // console.log(`text: ${textWidth} - container: ${containerWidth}`);
            if (textWidth <= containerWidth) {
                // console.log(`n: ${n} - i: ${i} - 1ER SALIDA`);
                span.style.fontSize = newFontSize + "px";
                span.textContent = texto;
                return;
            }

            if (i == 2) {
                // console.log(`n: ${n} - i: ${i} - SEGUNDA SALIDA`);
                let ratio = containerWidth / textWidth;
                let nChars = Math.floor(texto.length * ratio * 2) - 3;

                for (let j = nChars; j >= 0; j--) {
                    if (texto[j] == " ") {
                        nChars = j;
                        break;
                    }
                }

                if (nChars < 0) nChars = 0;
                span.textContent = texto.substring(0, nChars) + "...";
                span.style.fontSize = newFontSize + "px";
            }
        }

        n++;
    });
}

window.addEventListener("resize", fixText);

// ---------------------------
//           START
// ---------------------------

const       image_A = document.querySelector("#side-A     img");
const artist_span_A = document.querySelector("#side-A .artist");
const   song_span_A = document.querySelector("#side-A   .song");
const  album_span_A = document.querySelector("#side-A  .album");
const   info_span_A = document.querySelector("#side-A   .info");

const       image_B = document.querySelector("#side-B     img");
const artist_span_B = document.querySelector("#side-B .artist");
const   song_span_B = document.querySelector("#side-B   .song");
const  album_span_B = document.querySelector("#side-B  .album");
const   info_span_B = document.querySelector("#side-B   .info");

// let track_times = {};
// track_times["A"] = 0;
// track_times["B"] = 0;

function loadA(respA) {
    image_A.src = respA.img_url;
    artist_span_A.textContent = respA.artist;
    album_span_A.textContent = respA.album;
    song_span_A.textContent = respA.song;

    let minutes_A = Math.floor(respA.duration / 60);
    let seconds_A = (respA.duration % 60).toString().padStart(2, "0");
    info_span_A.textContent = `${respA.release} · ${minutes_A}:${seconds_A}`

    song_span_A.dataset.track_id = respA.id;
}

function loadB(respB) {
    image_B.src = respB.img_url;
    artist_span_B.textContent = respB.artist;
    album_span_B.textContent = respB.album;
    song_span_B.textContent = respB.song;

    let minutes_B = Math.floor(respB.duration / 60);
    let seconds_B = (respB.duration % 60).toString().padStart(2, "0");
    info_span_B.textContent = `${respB.release} · ${minutes_B}:${seconds_B}`

    song_span_A.dataset.trackId = respB.id;
}

fetch(`/game/start`)
    .then(response => response.json())
    .then(resp => {

        loadA(resp.A);
        loadB(resp.B);

        // document.querySelectorAll("span.artist").forEach(span => { span.style.fontSize = "5vh"; });
        // document.querySelectorAll(  "span.song").forEach(span => { span.style.fontSize = "7vh"; });
        // document.querySelectorAll( "span.album").forEach(span => { span.style.fontSize = "4vh"; });
        // document.querySelectorAll(  "span.info").forEach(span => { span.style.fontSize = "2vh"; });

        spans.forEach(span => {
            span.dataset.fullText = span.textContent;
        });

        fixText();
    });

// ---------------------------
//          CLICKS
// ---------------------------

const sides = document.querySelectorAll(".side")

sides.forEach(side => {
    side.addEventListener("click", () => {
        const sideCode = side.dataset.side;
        fetch(`/game/click?side=${sideCode}`)
            .then(response => response.json())
            .then(resp => {

                if (resp.finished) {
                    window.location.href = resp.redirect;
                } else {
                    loadA(resp.A);
                    loadB(resp.B);

                    spans.forEach(span => {
                        span.dataset.fullText = span.textContent;
                    });

                    fixText();
                }
                
                // if (resp.side_to_update == "A") {
                //     loadA(resp.data);
                // } else if (resp.side_to_update == "B") {
                //     loadB(resp.data)
                // } else {
                //     console.log("wtf did you send bro?")
                // }
            });
    });
});

// --------------------------------
//             SONGS
// --------------------------------

const songDatasCircles = document.querySelectorAll(".song-data .audio-play");

songDatasCircles.forEach(AudioPlay => {
    AudioPlay.addEventListener("mouseenter", () => {
        // console.log("ENTER")
        const sideCode = AudioPlay.closest(".side").dataset.side;
        fetch(`/game/play?side=${sideCode}&volume=${slider.value}`)
    });

    AudioPlay.addEventListener("mouseleave", () => {
        // console.log("LEAVE")
        const sideCode = AudioPlay.closest(".side").dataset.side;
        fetch(`/game/pause?side=${sideCode}&volume=${slider.value}`)
    });
});

// ------------------------------------
//                EXIT
// ------------------------------------

const exitButton = document.querySelector("#exit");

exitButton.addEventListener("click", () => {
    fetch(`/game/download-backup`)
        .then(response => {
            const disposition = response.headers.get("Content-Disposition");
            let filename = "backup.json";

            if (disposition && disposition.includes("filename=")) {
                filename = disposition
                    .split("filename=")[1]
                    .replace(/['"]/g, "");
            }

            return response.blob().then(blob => ({ blob, filename }));
        })
        .then(({ blob, filename }) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");

            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);

            window.location.href = "/game/exit";
        });
});