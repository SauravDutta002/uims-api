// Using import.meta.env for Vite environment variables
// In production, VITE_API_URL should be set to the Render backend URL (e.g. https://uims-api.onrender.com)
// In development, it defaults to an empty string to use the local Vite proxy
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
