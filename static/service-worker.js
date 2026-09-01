const CACHE_NAME = "myfarm-v1";

self.addEventListener("install", event => {
    console.log("MyFarm service worker installed");
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("MyFarm service worker activated");
    event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});