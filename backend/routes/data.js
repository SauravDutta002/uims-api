const express = require('express');
const { fetchAllData } = require('../cuims/scraper');

const router = express.Router();

// Middleware to check session token
function requireSession(sessions) {
  return (req, res, next) => {
    const token = req.headers['x-session-token'];
    if (!token || !sessions.has(token)) {
      return res.status(401).json({
        success: false,
        error: 'Invalid or expired session. Please login again.',
      });
    }
    req.session = sessions.get(token);
    next();
  };
}

/**
 * GET /api/refresh
 * Re-fetches all data from CUIMS using the stored session.
 */
router.get('/refresh', async (req, res) => {
  try {
    const data = await fetchAllData(req.session.cuimsSession);
    req.session.data = data; // Update cached data
    res.json({ success: true, data });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: 'Failed to refresh data. Session may have expired.',
    });
  }
});

module.exports = { router, requireSession };
