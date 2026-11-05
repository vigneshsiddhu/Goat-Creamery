from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect


def health(request):
    return JsonResponse({"status": "ok"})


def home(request):
    return redirect('dashboard')


def service_worker(request):
    js = """
    const CACHE_NAME = "myfarm-v1";

    self.addEventListener("install", event => {
        console.log("MyFarm Service Worker installed");
        self.skipWaiting();
    });

    self.addEventListener("activate", event => {
        console.log("MyFarm Service Worker activated");
        event.waitUntil(self.clients.claim());
    });

    self.addEventListener("fetch", event => {
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(event.request);
            })
        );
    });
    """

    return HttpResponse(
        js,
        content_type="application/javascript"
    )