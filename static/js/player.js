/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 Player

 The browser never plays audio - it only reflects and
 commands the mpv instance running on the Raspberry Pi
 through the /player/* API.

 Version : 0.3
===========================================================
*/

const SLEEP_PRESETS = [0, 15, 30, 45, 60];

class MusicPlayer {

    constructor() {

        this.playButton = document.getElementById("play-button");
        this.previousButton = document.getElementById("previous-button");
        this.nextButton = document.getElementById("next-button");

        this.shuffleButton = document.getElementById("shuffle-button");
        this.repeatButton = document.getElementById("repeat-button");
        this.queueButton = document.getElementById("queue-button");
        this.radioButton = document.getElementById("radio-button");
        this.sleepButton = document.getElementById("sleep-button");
        this.sleepLabel = document.getElementById("sleep-label");

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

        // Fullscreen "now playing"
        this.npView = document.getElementById("now-playing-view");
        this.npClose = document.getElementById("np-close");
        this.npCover = document.getElementById("np-cover");
        this.npCoverPlaceholder = document.getElementById("np-cover-placeholder");
        this.npTitle = document.getElementById("np-title");
        this.npArtist = document.getElementById("np-artist");
        this.npSlot = document.getElementById("np-slot");
        this.trackTrigger = document.getElementById("player-track-trigger");

        this.playerCenter = document.querySelector(".player-center");
        this.playerBar = document.getElementById("player-bar");
        this.playerButtonsEl = document.querySelector(".player-buttons");
        this.playerProgressEl = document.querySelector(".player-progress");
        this.playerExtraEl = document.querySelector(".player-extra");

        if (!this.playButton) {
            return;
        }

        this.state = null;
        this.volumeDragging = false;
        this.sleepIndex = 0;

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
        this.radioButton.addEventListener("click", () => this.run(Api.toggleRadio()));

        this.sleepButton.addEventListener("click", () => {
            this.sleepIndex = (this.sleepIndex + 1) % SLEEP_PRESETS.length;
            const minutes = SLEEP_PRESETS[this.sleepIndex];

            if (minutes === 0) {
                this.run(Api.cancelSleep());
            } else {
                this.run(Api.setSleep(minutes));
            }
        });

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

        this.trackTrigger.addEventListener("click", () => this.expand());
        this.npClose.addEventListener("click", () => this.collapse());
    }

    expand() {
        this.npSlot.appendChild(this.playerButtonsEl);
        this.npSlot.appendChild(this.playerProgressEl);
        this.npSlot.appendChild(this.playerExtraEl);
        this.npView.hidden = false;
    }

    collapse() {
        this.playerCenter.appendChild(this.playerButtonsEl);
        this.playerCenter.appendChild(this.playerProgressEl);
        this.playerBar.appendChild(this.playerExtraEl);
        this.npView.hidden = true;
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
            this.npTitle.textContent = track.title || "—";
            this.npArtist.textContent = track.artist || "—";

            if (track.coverArt) {
                this.cover.src = `/cover/${track.coverArt}`;
                this.cover.hidden = false;
                this.coverPlaceholder.style.display = "none";
                this.npCover.src = `/cover/${track.coverArt}`;
                this.npCover.hidden = false;
                this.npCoverPlaceholder.style.display = "none";
            } else {
                this.cover.hidden = true;
                this.coverPlaceholder.style.display = "flex";
                this.npCover.hidden = true;
                this.npCoverPlaceholder.style.display = "flex";
            }
        } else {
            this.title.textContent = "Ничего не играет";
            this.artist.textContent = "Выберите трек";
            this.npTitle.textContent = "Ничего не играет";
            this.npArtist.textContent = "Выберите трек";
            this.cover.hidden = true;
            this.coverPlaceholder.style.display = "flex";
            this.npCover.hidden = true;
            this.npCoverPlaceholder.style.display = "flex";
        }

        this.playButton.textContent = state.paused ? "▶" : "⏸";

        this.shuffleButton.classList.toggle("on", !!state.shuffle);
        this.repeatButton.classList.toggle("on", !!state.repeat && state.repeat !== "off");
        this.repeatButton.textContent = state.repeat === "one" ? "🔂" : "🔁";
        this.radioButton.classList.toggle("on", !!state.radio);

        if (state.sleep_remaining === null || state.sleep_remaining === undefined) {
            this.sleepLabel.textContent = "Сон";
            this.sleepButton.classList.remove("on");
        } else {
            this.sleepLabel.textContent = `${Math.ceil(state.sleep_remaining / 60)}м`;
            this.sleepButton.classList.add("on");
        }

        if (!this.volumeDragging) {
            this.volumeSlider.value = state.volume ?? 70;
        }

        this.setProgressUI(state.position || 0, state.duration || 0);

        if (!this.queuePanel.hidden) {
            this.renderQueue();
        }

        this.syncNowPlayingBadges();
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

    syncNowPlayingBadges() {
        const track = this.state && this.state.track;
        const trackId = track ? String(track.id) : null;
        const albumId = track && track.albumId ? String(track.albumId) : null;

        document.querySelectorAll("[data-play-id]").forEach((el) => {
            let match = false;

            if (track) {
                if (el.dataset.trackId !== undefined) {
                    match = el.dataset.trackId === trackId;
                } else if (el.dataset.playKind === "track") {
                    match = el.dataset.playId === trackId;
                } else if (el.dataset.playKind === "album") {
                    match = albumId !== null && el.dataset.playId === albumId;
                }
            }

            el.classList.toggle("is-playing", match);
        });
    }
}

const player = new MusicPlayer();
