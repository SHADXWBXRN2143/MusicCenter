/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 Favorites & Playlists

 Delegated handlers for star toggles and the "add to
 playlist" popover, plus the create/delete/remove actions
 on the playlist pages.

 Version : 0.1
===========================================================
*/

let playlistPopover = null;

function closePlaylistPopover() {
    if (playlistPopover) {
        playlistPopover.remove();
        playlistPopover = null;
    }
}

async function openPlaylistPopover(anchorEl, songId) {
    closePlaylistPopover();

    const res = await Api.playlists();
    const playlists = (res && res.playlists) || [];

    const box = document.createElement("div");
    box.className = "search-suggestions playlist-popover";

    const createItem = document.createElement("div");
    createItem.className = "suggestion-item";
    createItem.innerHTML = '<div class="suggestion-type"><svg class="icon"><use href="/static/icons/sprite.svg#plus"></use></svg></div><div><strong>Новый плейлист</strong></div>';

    createItem.addEventListener("click", async () => {
        const name = prompt("Название плейлиста:");

        if (!name) {
            return;
        }

        closePlaylistPopover();
        const created = await Api.createPlaylist(name, songId);

        if (created && created.success) {
            Toast.show(`Добавлено в «${name}»`);
        } else {
            Toast.error("Не удалось создать плейлист");
        }
    });

    box.appendChild(createItem);

    playlists.forEach((playlist) => {
        const item = document.createElement("div");
        item.className = "suggestion-item";

        item.innerHTML = `
            <div class="suggestion-type"><svg class="icon"><use href="/static/icons/sprite.svg#playlist"></use></svg></div>
            <div>
                <strong>${playlist.name}</strong>
                <small>${playlist.songCount || 0} треков</small>
            </div>
        `;

        item.addEventListener("click", async () => {
            closePlaylistPopover();
            const added = await Api.addToPlaylist(playlist.id, songId);

            if (added && added.success) {
                Toast.show(`Добавлено в «${playlist.name}»`);
            } else {
                Toast.error("Не удалось добавить в плейлист");
            }
        });

        box.appendChild(item);
    });

    document.body.appendChild(box);
    playlistPopover = box;

    const rect = anchorEl.getBoundingClientRect();
    box.style.position = "fixed";
    box.style.right = "auto";
    box.style.top = `${Math.min(rect.bottom + 6, window.innerHeight - 300)}px`;
    box.style.left = `${Math.max(8, Math.min(rect.left, window.innerWidth - 370))}px`;
}

document.addEventListener("click", async (event) => {

    // Favorite star toggle (cards, rows, album/artist headers)
    const starEl = event.target.closest("[data-star-id]");

    if (starEl) {
        event.preventDefault();
        event.stopPropagation();

        const id = starEl.dataset.starId;
        const kind = starEl.dataset.starKind || "song";
        const wasActive = starEl.classList.contains("active");
        const labelEl = starEl.querySelector(".fav-toggle-label");

        starEl.classList.toggle("active", !wasActive);

        if (labelEl) {
            labelEl.textContent = wasActive ? "В избранное" : "В избранном";
        }

        const res = wasActive ? await Api.unstar(id, kind) : await Api.star(id, kind);

        if (!res || !res.success) {
            starEl.classList.toggle("active", wasActive);

            if (labelEl) {
                labelEl.textContent = wasActive ? "В избранном" : "В избранное";
            }

            Toast.error("Не удалось обновить избранное");
        }

        return;
    }

    // "Add to playlist" trigger
    const queueEl = event.target.closest("[data-queue-id]");

    if (queueEl) {
        event.preventDefault();
        event.stopPropagation();
        openPlaylistPopover(queueEl, queueEl.dataset.queueId);
        return;
    }

    // Remove a track from the currently open playlist
    const removeEl = event.target.closest("[data-remove-playlist-id]");

    if (removeEl) {
        event.preventDefault();
        event.stopPropagation();

        const playlistId = removeEl.dataset.removePlaylistId;
        const index = Number(removeEl.dataset.removeIndex);
        const res = await Api.removeFromPlaylist(playlistId, index);

        if (res && res.success) {
            removeEl.closest(".track-row")?.remove();
        } else {
            Toast.error("Не удалось убрать трек из плейлиста");
        }

        return;
    }

    // Create a new (empty) playlist
    if (event.target.closest("#create-playlist-btn")) {
        const name = prompt("Название плейлиста:");

        if (!name) {
            return;
        }

        const res = await Api.createPlaylist(name);

        if (res && res.success && res.playlist && res.playlist.id) {
            window.location = `/playlists/${res.playlist.id}`;
        } else {
            Toast.error("Не удалось создать плейлист");
        }

        return;
    }

    // Delete the currently open playlist
    const deleteBtn = event.target.closest("#delete-playlist-btn");

    if (deleteBtn) {
        if (!confirm("Удалить этот плейлист?")) {
            return;
        }

        const res = await Api.deletePlaylist(deleteBtn.dataset.playlistId);

        if (res && res.success) {
            window.location = "/playlists";
        } else {
            Toast.error("Не удалось удалить плейлист");
        }

        return;
    }

    if (playlistPopover && !playlistPopover.contains(event.target)) {
        closePlaylistPopover();
    }
});
