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
    toggleRadio() { return this.post("/player/radio"); },
    setEq(preset) { return this.post("/player/eq", { preset }); },
    playerLevels() { return this.get("/player/levels"); },
    setSleep(minutes) { return this.post("/player/sleep", { minutes }); },
    cancelSleep() { return this.post("/player/sleep/cancel"); },
    queueAdd(payload) { return this.post("/player/queue/add", payload); },
    queueClear() { return this.post("/player/queue/clear"); },

    // Search
    search(query) { return this.get(`/search/api?q=${encodeURIComponent(query)}`); },
    suggestions(query) { return this.get(`/search/suggestions?q=${encodeURIComponent(query)}`); },

    // Favorites
    star(id, kind = "song") { return this.post("/favorites/star", { id, kind }); },
    unstar(id, kind = "song") { return this.post("/favorites/unstar", { id, kind }); },

    // Playlists
    playlists() { return this.get("/playlists/api"); },
    createPlaylist(name, songId) { return this.post("/playlists/create", { name, song_id: songId }); },
    addToPlaylist(playlistId, songId) { return this.post(`/playlists/${playlistId}/add`, { song_id: songId }); },
    removeFromPlaylist(playlistId, index) { return this.post(`/playlists/${playlistId}/remove`, { index }); },
    deletePlaylist(playlistId) { return this.post(`/playlists/${playlistId}/delete`); },
};

window.Api = Api;
