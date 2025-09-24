const response_span = document.querySelector("span.response");

function turnToPlaylist() {
    fetch("/end/turn_playlist")
        .then(response => {
            response_span.textContent = response.ok ? 
                "Playlist successfully created." : 
                "There was an error creating the playlist.";
        });
}

const list = document.querySelector("ol.list");

for (const song of window.SONGS) {
    const new_li = document.createElement("li");
    new_li.textContent = song;
    list.appendChild(new_li);
}