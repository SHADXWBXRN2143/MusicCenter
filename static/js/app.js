/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 App-wide behaviour: toasts and "play" click delegation
 for cards, rows and track lists.

 Version : 0.2
===========================================================
*/

if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/sw.js").catch((error) => {
            console.error("Service worker registration failed:", error);
        });
    });
}

window.Toast = {
    show(message, type = "info") {
        const stack = document.getElementById("toast-stack");

        if (!stack) {
            return;
        }

        const el = document.createElement("div");
        el.className = `toast ${type}`;
        el.textContent = message;

        stack.appendChild(el);

        setTimeout(() => el.remove(), 3000);
    },

    error(message) {
        this.show(message, "error");
    },
};

document.addEventListener("click", async (event) => {
    if (event.target.closest("[data-star-id], [data-queue-id], [data-remove-playlist-id]")) {
        return;
    }

    const el = event.target.closest("[data-play-kind]");

    if (!el) {
        return;
    }

    event.preventDefault();
    event.stopPropagation();

    const kind = el.dataset.playKind;
    const id = el.dataset.playId;

    const payload = { kind, id };

    if (el.dataset.playIndex !== undefined) {
        payload.index = Number(el.dataset.playIndex);
    }

    const res = await Api.play(payload);

    if (res && res.success) {
        const title = res.state && res.state.track ? res.state.track.title : null;
        Toast.show(title ? `Играет: ${title}` : "Воспроизведение началось");
    } else {
        Toast.error((res && res.message) || "Не удалось запустить воспроизведение");
    }
});
