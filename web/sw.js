/* 投资词典 Invest Dictionary - Service Worker (T6 PWA)
 * 缓存优先策略：先网络、离线回退缓存。
 */
const CACHE = 'dict-v1';
const PRECACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  // 动态词条页：网络优先，失败回退首页
  event.respondWith(
    fetch(req).then((resp) => {
      if (resp && resp.status === 200) {
        const clone = resp.clone();
        caches.open(CACHE).then((cache) => cache.put(req, clone));
      }
      return resp;
    }).catch(() => caches.match(req).then((hit) => hit || caches.match('/')))
  );
});
