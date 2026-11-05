import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const frontend = fileURLToPath(new URL('.', import.meta.url));
export default defineConfig(({ command }) => {
  const workspace = resolve(process.env.COULDHAPPEN_ROOT || resolve(frontend, '..'));
  const connectionPath = resolve(workspace, '.couldhappen/connection.json');
  const connection = command === 'serve' && existsSync(connectionPath) ? JSON.parse(readFileSync(connectionPath, 'utf8')) : null;
  const address = connection?.address;
  if (address && !/^http:\/\/127\.0\.0\.1:\d+$/.test(address)) throw new Error('Expected loopback helper address');
  return {
    root: frontend, publicDir: false,
    plugins: [svelte(), {
      name: 'public-boundary',
      configureServer(server) {
        if (!address) throw new Error('Start the workspace helper before Vite');
        server.middlewares.use((req, res, next) => {
          let path;
          try { path = decodeURIComponent((req.url || '/').split('?')[0]).replaceAll('\\', '/'); }
          catch { res.statusCode = 400; res.end(); return; }
          // Disallow arbitrary filesystem imports even from accidentally authored source.
          if (path.startsWith('/@fs/') || /(?:^|\/)(?:imports|public|\.couldhappen|\.git|\.env[^/]*|START_HERE\.md)(?:\/|$)/i.test(path) ||
              path === '/control' || (path.startsWith('/api/') && !/^\/api\/(?:snapshot$|entries$|assets\/)/.test(path))) {
            res.statusCode = 403; res.end('Private path unavailable'); return;
          }
          next();
        });
      }
    }],
    server: {
      host: '127.0.0.1', port: 5173, strictPort: true,
      fs: { strict: true, allow: [frontend], deny: ['**/.env*', '**/.git/**', '**/.couldhappen/**', '**/imports/**', '**/public/**'] },
      proxy: address ? {
        '^/api/snapshot$': { target: address, changeOrigin: true },
        '^/api/entries$': { target: address, changeOrigin: true },
        '^/api/assets/': { target: address, changeOrigin: true }
      } : {}
    }
  };
});
