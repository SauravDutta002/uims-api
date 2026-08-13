const sharp = require('sharp');
const Tesseract = require('tesseract.js');

let worker = null;

/**
 * Initialize the Tesseract OCR worker (singleton).
 * Kept alive for the lifetime of the server to avoid re-init cost.
 */
async function initWorker() {
  if (!worker) {
    console.log('[Captcha] Initializing Tesseract.js worker...');
    worker = await Tesseract.createWorker('eng');
    await worker.setParameters({
      tessedit_char_whitelist:
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
    });
    console.log('[Captcha] Worker ready.');
  }
  return worker;
}

/**
 * Solve a CUIMS captcha image.
 * @param {Buffer} imageBuffer - Raw JPEG/PNG buffer of the captcha
 * @returns {string} Recognized captcha text (4-6 chars)
 */
async function solveCaptcha(imageBuffer) {
  // Step 1: Preprocess the image with Sharp
  // The CUIMS captcha has dark text on light dotted background
  const processed = await sharp(imageBuffer)
    .grayscale() // Remove color
    .resize(200, 60, { fit: 'fill' }) // Upscale 2x for better OCR
    .median(3) // Remove salt-and-pepper noise (dots)
    .threshold(140) // Binarize: text → black, background → white
    .sharpen() // Sharpen edges
    .toBuffer();

  // Step 2: OCR with Tesseract
  const w = await initWorker();
  const {
    data: { text },
  } = await w.recognize(processed);

  // Step 3: Clean up result
  const cleaned = text.trim().replace(/[^A-Za-z0-9]/g, '');

  return cleaned;
}

module.exports = { solveCaptcha, initWorker };
