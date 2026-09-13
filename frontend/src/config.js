/**
 * NyayaAI Frontend Runtime Configuration
 * Centralized API base URL with fallback for local development.
 */

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

export const API_ENDPOINTS = {
  query: `${API_BASE_URL}/api/query`,
  route: `${API_BASE_URL}/api/route`,
  states: `${API_BASE_URL}/api/states`,
  authorities: `${API_BASE_URL}/api/authorities`,
  provisions: `${API_BASE_URL}/api/provisions`,
  health: `${API_BASE_URL}/api/health`,
};
