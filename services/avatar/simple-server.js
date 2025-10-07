const http = require('http');
const port = 8008;

const emotionProfiles = {
  happy: { color: '#10B981', intensity: 0.8 },
  excited: { color: '#F59E0B', intensity: 1.0 },
  confident: { color: '#3B82F6', intensity: 0.75 },
  curious: { color: '#8B5CF6', intensity: 0.85 },
  proud: { color: '#EC4899', intensity: 0.8 },
  optimistic: { color: '#84CC16', intensity: 0.85 }
};

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ service: 'avatar', status: 'healthy', timestamp: new Date().toISOString() }));
  } else if (req.url === '/animation/emotion' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      const data = JSON.parse(body);
      const profile = emotionProfiles[data.emotion] || emotionProfiles.optimistic;
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, animation: profile }));
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(port, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎭 JarvisX Avatar Service (Simple Mode)                ║
║                                                           ║
║   Status: ACTIVE                                         ║
║   Port: ${port}                                           ║
║   Mode: Standalone (no dependencies required)            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});
