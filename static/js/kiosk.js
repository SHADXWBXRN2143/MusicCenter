/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 Kiosk Screen

 Standalone poll/control loop for the small-screen "now
 playing" page - independent of player.js, which assumes
 the full site's sidebar/queue/now-playing DOM.

 Version : 0.1
===========================================================
*/

class KioskPlayer {

    constructor() {
        this.cover = document.getElementById("kiosk-cover");
        this.coverPlaceholder = document.getElementById("kiosk-cover-placeholder");
        this.title = document.getElementById("kiosk-title");
        this.artist = document.getElementById("kiosk-artist");

        this.progressFill = document.getElementById("kiosk-progress-fill");
        this.currentTimeEl = document.getElementById("kiosk-current-time");
        this.totalTimeEl = document.getElementById("kiosk-total-time");

        this.playButton = document.getElementById("kiosk-play");
        this.playIconUse = document.getElementById("kiosk-play-icon");
        this.prevButton = document.getElementById("kiosk-prev");
        this.nextButton = document.getElementById("kiosk-next");

        this.clock = document.getElementById("kiosk-clock");
        this.banner = document.getElementById("kiosk-banner");
        this.waveform = document.getElementById("kiosk-waveform");
        this.ambientBg = document.getElementById("ambient-bg");
        this._ambientCoverArt = null;

        this.state = null;
        this._localPosition = 0;
        this._localTimestamp = performance.now();

        this.bindEvents();
        this.poll();
        this.updateClock();

        setInterval(() => this.poll(), 1000);
        setInterval(() => this.updateClock(), 1000);
        setInterval(() => this.pollLevels(), 120);
        requestAnimationFrame(() => this.tick());
    }

    bindEvents() {
        this.playButton.addEventListener("click", () => this.run(Api.toggle()));
        this.prevButton.addEventListener("click", () => this.run(Api.previous()));
        this.nextButton.addEventListener("click", () => this.run(Api.next()));
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
            this.artist.textContent = "MusicCenter";
            this.cover.hidden = true;
            this.coverPlaceholder.style.display = "flex";
        }

        this.playIconUse.setAttribute(
            "href",
            `/static/icons/sprite.svg#${state.paused ? "play" : "pause"}`
        );
        this.waveform.classList.toggle("paused", !!state.paused || !track);

        if (state.paused || !track) {
            this.waveform.classList.remove("live");
        }

        this.updateAmbient(track);
        this.setProgressUI(state.position || 0, state.duration || 0);
    }

    async pollLevels() {
        if (!this.state || this.state.paused || !this.state.track) {
            return;
        }

        const res = await Api.playerLevels();

        if (res && res.success && res.available && res.levels && res.levels.length) {
            this.renderLevels(res.levels);
        }
    }

    renderLevels(levels) {
        const bars = this.waveform.querySelectorAll("span");

        this.waveform.classList.add("live");

        bars.forEach((bar, index) => {
            const value = levels[index % levels.length] || 0;
            bar.style.height = `${8 + value * 92}%`;
        });
    }

    updateAmbient(track) {
        if (!this.ambientBg) {
            return;
        }

        const coverArt = track && track.coverArt;

        if (coverArt === this._ambientCoverArt) {
            return;
        }

        this._ambientCoverArt = coverArt || null;
        this.ambientBg.style.backgroundImage = coverArt ? `url(/cover/${coverArt})` : "";
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

    updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, "0");
        const minutes = String(now.getMinutes()).padStart(2, "0");
        this.clock.textContent = `${hours}:${minutes}`;
    }
}

const kioskPlayer = new KioskPlayer();
