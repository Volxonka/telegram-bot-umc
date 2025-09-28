// Enhanced Service Worker for УМЦ Web App based on Context7 optimizations
const CACHE_NAME = 'umc-webapp-v2';
const urlsToCache = [
    '/',
    '/enhanced.html',
    '/enhanced-styles.css',
    '/enhanced-app.js',
    '/mobile-test.html',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://telegram.org/js/telegram-web-app.js'
];

// Performance optimization for mobile devices
const CACHE_STRATEGY = {
    CACHE_FIRST: 'cache-first',
    NETWORK_FIRST: 'network-first',
    STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};

// Install event
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Enhanced fetch event with Context7 mobile optimizations
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Different strategies based on resource type
    if (url.pathname.endsWith('.html') || url.pathname === '/') {
        // HTML files: Network first with cache fallback
        event.respondWith(networkFirstStrategy(request));
    } else if (url.pathname.endsWith('.css') || url.pathname.endsWith('.js')) {
        // Static assets: Cache first
        event.respondWith(cacheFirstStrategy(request));
    } else if (url.hostname === 'cdnjs.cloudflare.com' || url.hostname === 'telegram.org') {
        // External resources: Stale while revalidate
        event.respondWith(staleWhileRevalidateStrategy(request));
    } else {
        // Default: Network first
        event.respondWith(networkFirstStrategy(request));
    }
});

// Cache first strategy for static assets
async function cacheFirstStrategy(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('Cache first strategy failed:', error);
        return new Response('Offline', { status: 503 });
    }
}

// Network first strategy for dynamic content
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        return new Response('Offline', { status: 503 });
    }
}

// Stale while revalidate strategy for external resources
async function staleWhileRevalidateStrategy(request) {
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    }).catch(() => cachedResponse);
    
    return cachedResponse || fetchPromise;
}

// Activate event
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
