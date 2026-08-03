/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 Service Worker

 Only caches static assets (CSS/JS/manifest) so the app is
 installable. Pages, /player/*, /cover/*, /search/* always
 go to the network - this is a live remote control, cached
 player state would just be confusing.

 Version : 0.1
===========================================================
*/

// Bump this whenever static CSS/JS changes ship, or installed clients
// keep serving the old cached files indefinitely.
const CACHE_NAME = "musiccenter-static-v3";

const STATIC_ASSETS = [
    "/static/css/base.css",
    "/static/css/layout.css",
    "/static/css/sidebar.css",
    "/static/css/cards.css",
    "/static/css/album.css",
    "/static/css/search.css",
    "/static/css/player.css",
    "/static/css/animations.css",
    "/static/js/api.js",
    "/static/js/player.js",
    "/static/js/search.js",
    "/static/js/library.js",
    "/static/js/app.js",
    "/static/manifest.json",
    "/static/icons/icon.svg",
    "/static/icons/sprite.svg",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
        ))
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    const url = new URL(event.request.url);

    if (event.request.method !== "GET" || !url.pathname.startsWith("/static/")) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) {
                return cached;
            }

            return fetch(event.request).then((response) => {
                const copy = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
                return response;
            });
        })
    );
});
