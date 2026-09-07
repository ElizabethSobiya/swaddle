/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Origin of the deployed API, e.g. https://swaddle-api.up.railway.app.
   * Empty in development, where Vite proxies /api to localhost:8001. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
