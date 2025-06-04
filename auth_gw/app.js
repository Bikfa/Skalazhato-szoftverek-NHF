// Egyszerű Express + http-proxy-middleware + JWT alapú auth

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
const log4js = require('log4js');                             

const app = express();
const port = process.env.PORT || 4000; 

// A környezeti változók: BACKEND_URL és JWT_SECRET docker-compose-ból érkezik
const BACKEND_URL = process.env.BACKEND_URL;   
const JWT_SECRET = process.env.JWT_SECRET;     

if (!BACKEND_URL || !JWT_SECRET) {
  console.error("Nincs beállítva BACKEND_URL vagy JWT_SECRET!");
  process.exit(1);
}

app.use(bodyParser.json());

// Dummy admin user
const DUMMY_USER = {
  email: "admin@test.com",
  password: "admin",
  id: 1
};

const logger = log4js.getLogger();
logger.lever = 'debug';

// 1) /auth útvonal – ide kell POST-tal elküldeni { email, password }, visszaad egy JWT-t
app.post('/auth', (req, res) => {
  const { email, password } = req.body;
  if (email === DUMMY_USER.email && password === DUMMY_USER.password) {
    const payload = { userId: DUMMY_USER.id, email: DUMMY_USER.email };
    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '8h' });
    return res.json({ token });
  }
  return res.status(401).json({ error: 'Invalid credentials' });
});

// 2) Middleware a JWT ellenőrzésére a többi útvonal előtt
function checkAuthHeader(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid Authorization header' });
  }
  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    next();
  } catch (err) {
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
}

// Ha a kérés nem /auth, akkor kitesszük a checkAuthHeader-t
app.use((req, res, next) => {
  if (req.path === '/auth') return next();
  return checkAuthHeader(req, res, next);
});

// 3) Minden más kérést proxylunk a BACKEND_URL felé
app.use('/', createProxyMiddleware({
  target: BACKEND_URL,
  logger,
  changeOrigin: true,
  on: {
      proxyReq: (proxyReq, req, res) => {
          console.log(`[ProxyReq] ${req.method} ${req.originalUrl}`);
          if ( req.body && (req.method === 'POST' || req.method === 'PUT' || req.method === 'PATCH') ) {
              const bodyData = JSON.stringify(req.body)
              proxyReq.setHeader('Content-Type', 'application/json')
              proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData))
              proxyReq.write(bodyData)
          }
      },
      error: (err, req, res) => {
        res.status(500).json({ error: 'Proxy error', details: err.message });
      },
      // Optional: Log proxy response status
      proxyRes: (proxyRes, req, res) => {
        console.log(`[ProxyRes] ${req.method} ${req.originalUrl} -> ${proxyRes.statusCode}`);
      },
  }
}
))


app.listen(port, () => {
  console.log(`Auth GW listening on port ${port}`);
});
