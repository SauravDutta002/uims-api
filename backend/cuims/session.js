const axios = require('axios');

/**
 * CUIMSSession - Manages HTTP requests with automatic cookie handling.
 * Mirrors Python's requests.Session() behavior for the CUIMS portal.
 */
class CUIMSSession {
  constructor() {
    this.cookies = {};
  }

  /** Parse Set-Cookie headers and merge into cookie store */
  _updateCookies(response) {
    const setCookies = response.headers['set-cookie'];
    if (!setCookies) return;

    const cookieArray = Array.isArray(setCookies) ? setCookies : [setCookies];
    cookieArray.forEach((cookie) => {
      const [nameValue] = cookie.split(';');
      const eqIndex = nameValue.indexOf('=');
      if (eqIndex > 0) {
        const name = nameValue.substring(0, eqIndex).trim();
        const value = nameValue.substring(eqIndex + 1).trim();
        this.cookies[name] = value;
      }
    });
  }

  /** Build Cookie header string from stored cookies */
  getCookieString() {
    return Object.entries(this.cookies)
      .map(([name, value]) => `${name}=${value}`)
      .join('; ');
  }

  /**
   * Internal request method.
   * Always disables auto-redirect so we can handle 302s manually.
   */
  async _request(method, url, options = {}) {
    const config = {
      method,
      url,
      headers: {
        Cookie: this.getCookieString(),
        ...(options.headers || {}),
      },
      maxRedirects: 0,
      validateStatus: () => true, // Don't throw on any status code
    };

    if (options.data !== undefined) config.data = options.data;
    if (options.responseType) config.responseType = options.responseType;
    if (options.transformRequest) config.transformRequest = options.transformRequest;

    // For text responses, prevent axios from auto-parsing JSON
    if (!options.responseType || options.responseType === 'text') {
      config.transformResponse = [(data) => data];
    }

    const response = await axios(config);
    this._updateCookies(response);
    return response;
  }

  /** GET request */
  async get(url, options = {}) {
    return this._request('get', url, options);
  }

  /** POST with URL-encoded form data (like HTML form submission) */
  async postForm(url, formData) {
    const params = new URLSearchParams(formData);
    return this._request('post', url, {
      data: params.toString(),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  }

  /** POST with raw body string (used for CUIMS JSON-like endpoints) */
  async postRaw(url, rawBody, contentType = 'application/json') {
    return this._request('post', url, {
      data: rawBody,
      headers: { 'Content-Type': contentType },
      transformRequest: [(data) => data], // Send string as-is, don't serialize
    });
  }
}

module.exports = CUIMSSession;
