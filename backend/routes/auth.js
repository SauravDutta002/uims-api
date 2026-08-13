const express = require('express');
const { randomUUID } = require('crypto');
const { login, fetchAllData } = require('../cuims/scraper');

const router = express.Router();

// In-memory session store: token → { cuimsSession, data, loginTime }
const sessions = new Map();

/**
 * POST /api/login
 * Body: { uid: string, password: string }
 * Response: { success, token, data: { profile, attendance, marks, timetable } }
 */
router.post('/login', async (req, res) => {
  const { uid, password } = req.body;

  if (!uid || !password) {
    return res.status(400).json({
      success: false,
      error: 'UID and password are required',
    });
  }

  try {
    console.log(`[Auth] Login request for UID: ${uid}`);

    // Step 1: Login to CUIMS (with auto-captcha)
    const cuimsSession = await login(uid, password);

    // Step 2: Fetch all data
    console.log('[Auth] Fetching all data...');
    const data = await fetchAllData(cuimsSession);

    // Step 3: Create session token
    const token = randomUUID();
    sessions.set(token, {
      cuimsSession,
      data,
      uid,
      loginTime: Date.now(),
    });

    console.log(`[Auth] Login complete for ${uid}, token: ${token.slice(0, 8)}...`);

    res.json({
      success: true,
      token,
      data,
    });
  } catch (err) {
    console.error(`[Auth] Login failed for ${uid}:`, err.message);

    const status = err.code === 'INCORRECT_CREDENTIALS' ? 401 : 500;
    res.status(status).json({
      success: false,
      error: err.message || 'Login failed',
      code: err.code || 'UNKNOWN_ERROR',
    });
  }
});

/**
 * POST /api/logout
 */
router.post('/logout', (req, res) => {
  const token = req.headers['x-session-token'];
  if (token) sessions.delete(token);
  res.json({ success: true });
});

// Export sessions map for use in data routes
router.sessions = sessions;

module.exports = router;
