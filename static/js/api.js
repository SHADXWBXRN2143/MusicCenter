/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 API Helper

 Version : 0.2
===========================================================
*/

const Api = {

    async _request(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: { "Content-Type": "application/json" },
                ...options,
            });

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                if (window.Toast) {
                    window.Toast.error((data && data.message) || `Ошибка сервера (${response.status})`);
                }
                return data;
            }

            return data;
        } catch (error) {
            console.error("API error:", url, error);

            if (window.Toast) {
                window.Toast.error("Не удалось связаться с сервером");
            }

            return null;
        }
    },

    get(url) {
        return this._request(url);
    },

    post(url, body) {
        return this._request(url, {
            method: "POST",
            body: JSON.stringify(body || {}),
        });
    },

    // Player
    playerState() { return this.get("/player/state"); },
    play(payload) { return this.post("/player/play", payload); },
    toggle() { return this.post("/player/toggle"); },
    next() { return this.post("/player/next"); },
    previous() { return this.post("/player/previous"); },
    seek(position) { return this.post("/player/seek", { position }); },
    setVolume(value) { return this.post("/player/volume", { value }); },
    toggleShuffle() { return this.post("/player/shuffle"); },
    cycleRepeat() { return this.post("/player/repeat"); },
    queueAdd(payload) { return this.post("/player/queue/add", payload); },
    queueClear() { return this.post("/player/queue/clear"); },

    // Search
    search(query) { return this.get(`/search/api?q=${encodeURIComponent(query)}`); },
    suggestions(query) { return this.get(`/search/suggestions?q=${encodeURIComponent(query)}`); },
};

window.Api = Api;
