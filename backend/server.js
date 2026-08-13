const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/auth');
const { router: dataRoutes, requireSession } = require('./routes/data');
const { initWorker } = require('./cuims/captcha');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api', authRoutes);
app.use('/api', requireSession(authRoutes.sessions), dataRoutes);

// Health check
app.get('/api/health', (_, res) => {
  res.json({ status: 'ok', sessions: authRoutes.sessions.size });
});

// Start server
async function start() {
  // Pre-initialize the Tesseract worker so the first login is faster
  console.log('[Server] Pre-loading Tesseract OCR worker...');
  await initWorker();

  app.listen(PORT, () => {
    console.log(`[Server] CUIMS API running on http://localhost:${PORT}`);
  });
}

start().catch((err) => {
  console.error('[Server] Failed to start:', err);
  process.exit(1);
});
