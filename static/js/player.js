/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 Player

 The browser never plays audio - it only reflects and
 commands the mpv instance running on the Raspberry Pi
 through the /player/* API.

 Version : 0.2
===========================================================
*/

class MusicPlayer {

    constructor() {

        this.playButton = document.getElementById("play-button");
        this.previousButton = document.getElementById("previous-button");
        this.nextButton = document.getElementById("next-button");

        this.shuffleButton = document.getElementById("shuffle-button");
        this.repeatButton = document.getElementById("repeat-button");
        this.queueButton = document.getElementById("queue-button");

        this.volumeSlider = document.getElementById("volume-slider");

        this.progressBar = document.getElementById("progress-bar");
        this.progressFill = document.getElementById("progress-fill");
        this.progressHandle = document.getElementById("progress-handle");

        this.currentTimeEl = document.getElementById("current-time");
        this.totalTimeEl = document.getElementById("total-time");

        this.cover = document.getElementById("player-cover");
        this.coverPlaceholder = document.getElementById("player-cover-placeholder");
        this.title = document.getElementById("player-title");
        this.artist = document.getElementById("player-artist");

        this.banner = document.getElementById("player-banner");
        this.queuePanel = document.getElementById("queue-panel");
        this.queueList = document.getElementById("queue-list");

        if (!this.playButton) {
            return;
        }

        this.state = null;
        this.volumeDragging = false;

        this._localPosition = 0;
        this._localTimestamp = performance.now();

        this.bindEvents();
        this.poll();

        setInterval(() => this.poll(), 1000);
        requestAnimationFrame(() => this.tick());
    }

    bindEvents() {

        this.playButton.addEventListener("click", () => this.run(Api.toggle()));
        this.previousButton.addEventListener("click", () => this.run(Api.previous()));
        this.nextButton.addEventListener("click", () => this.run(Api.next()));
        this.shuffleButton.addEventListener("click", () => this.run(Api.toggleShuffle()));
        this.repeatButton.addEventListener("click", () => this.run(Api.cycleRepeat()));

        this.volumeSlider.addEventListener("input", () => {
            this.volumeDragging = true;
        });

        this.volumeSlider.addEventListener("change", (event) => {
            this.volumeDragging = false;
            this.run(Api.setVolume(Number(event.target.value)));
        });

        this.progressBar.addEventListener("click", (event) => {
            if (!this.state || !this.state.duration) {
                return;
            }

            const rect = this.progressBar.getBoundingClientRect();
            const percent = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
            const position = percent * this.state.duration;

            this._localPosition = position;
            this._localTimestamp = performance.now();
            this.setProgressUI(position, this.state.duration);

            this.run(Api.seek(position));
        });

        this.queueButton.addEventListener("click", () => {
            this.queuePanel.hidden = !this.queuePanel.hidden;

            if (!this.queuePanel.hidden) {
                this.renderQueue();
            }
        });
    }

    async run(promise) {
        const res = await promise;

        if (res && res.state) {
            this.applyState(res.state);
        }
    }

    async poll() {
        const res = await Api.playerState();

        if (res && res.success) {
            this.applyState(res.state);
        }
    }

    applyState(state) {
        this.state = state;

        this._localPosition = state.position || 0;
        this._localTimestamp = performance.now();

        this.banner.hidden = state.available !== false;

        const track = state.track;

        if (track) {
            this.title.textContent = track.title || "—";
            this.artist.textContent = track.artist || "—";

            if (track.coverArt) {
                this.cover.src = `/cover/${track.coverArt}`;
                this.cover.hidden = false;
                this.coverPlaceholder.style.display = "none";
            } else {
                this.cover.hidden = true;
                this.coverPlaceholder.style.display = "flex";
            }
        } else {
            this.title.textContent = "Ничего не играет";
            this.artist.textContent = "Выберите трек";
            this.cover.hidden = true;
            this.coverPlaceholder.style.display = "flex";
        }

        this.playButton.textContent = state.paused ? "▶" : "⏸";

        this.shuffleButton.classList.toggle("on", !!state.shuffle);
        this.repeatButton.classList.toggle("on", !!state.repeat && state.repeat !== "off");
        this.repeatButton.textContent = state.repeat === "one" ? "🔂" : "🔁";

        if (!this.volumeDragging) {
            this.volumeSlider.value = state.volume ?? 70;
        }

        this.setProgressUI(state.position || 0, state.duration || 0);

        if (!this.queuePanel.hidden) {
            this.renderQueue();
        }
    }

    tick() {
        if (this.state && !this.state.paused && this.state.duration) {
            const elapsed = (performance.now() - this._localTimestamp) / 1000;
            const position = Math.min(this.state.duration, this._localPosition + elapsed);
            this.setProgressUI(position, this.state.duration);
        }

        requestAnimationFrame(() => this.tick());
    }

    setProgressUI(position, duration) {
        const percent = duration ? Math.min(100, (position / duration) * 100) : 0;

        this.progressFill.style.width = `${percent}%`;
        this.progressHandle.style.left = `${percent}%`;

        this.currentTimeEl.textContent = this.formatTime(position);
        this.totalTimeEl.textContent = this.formatTime(duration);
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) {
            return "0:00";
        }

        const minutes = Math.floor(seconds / 60);
        const sec = Math.floor(seconds % 60);

        return `${minutes}:${String(sec).padStart(2, "0")}`;
    }

    renderQueue() {
        const tracks = (this.state && this.state.tracks) || [];

        this.queueList.innerHTML = "";

        if (tracks.length === 0) {
            this.queueList.innerHTML = '<div class="queue-empty">Очередь пуста</div>';
            return;
        }

        tracks.forEach((track, index) => {
            const item = document.createElement("div");
            item.className = "queue-item" + (index === this.state.index ? " active" : "");

            item.innerHTML = `
                <div>
                    ${track.title || "—"}
                    <small>${track.artist || ""}</small>
                </div>
            `;

            this.queueList.appendChild(item);
        });
    }
}

const player = new MusicPlayer();
