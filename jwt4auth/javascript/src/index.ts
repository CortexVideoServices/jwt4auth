const REFRESH_TOKEN_STORAGE_KEY = 'refresh_token';

/**
 * Token data
 */
export interface TokenData {
  [index: string]: any;
}

let refresh_token: string | null = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
let token_data: TokenData | null = null;
let on_refresh_fail: () => void = () => undefined;

/**
 * Wrapped `fetch`. In case of a 401 error, it tries to update the access token and retry the request.
 * @param input
 * @param init
 */
async function wrappedFetch(input: RequestInfo, init?: RequestInit): Promise<Response> {
  let resp = await fetch(input, init);
  if (resp.status === 401) {
    if (await refresh()) {
      resp = await fetch(input, init);
    }
  }
  return resp;
}

/**
 * User login (receives access and refresh tokens)
 * @param username
 * @param password
 * @param onRefreshFail callback will be called if  fails to restore the access token
 */
export async function login(username: string, password: string, onRefreshFail?: () => void) {
  if (onRefreshFail) on_refresh_fail = onRefreshFail;
  const resp = await fetch('/backend/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  if (resp.ok) {
    const data = await resp.json();
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, data.refresh_token);
    refresh_token = data.refresh_token;
    token_data = data.token_data;
    return true;
  }
  return false;
}

/**
 * Refreshes access token
 */
export async function refresh() {
  if (typeof refresh_token === 'string') {
    const resp = await fetch('/backend/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token }),
    });
    if (resp.ok) {
      const data = await resp.json();
      localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, data.refresh_token);
      refresh_token = data.refresh_token;
      token_data = data.token_data;
      return true;
    } else {
      localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
      refresh_token = null;
      token_data = null;
      on_refresh_fail();
    }
  }
  return false;
}

/**
 * User logoff (Reset access and refresh tokens)
 */
export async function logoff() {
  if (typeof refresh_token === 'string') {
    await wrappedFetch('/backend/logoff');
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
    refresh_token = null;
    token_data = null;
  }
}

/**
 * Returns token data
 */
export async function getTokenData() {
  if (
    typeof refresh_token === 'string' &&
    token_data !== null &&
    'exp' in token_data &&
    token_data.exp * 1000 > Date.now()
  ) {
    return token_data;
  }
  await refresh();
  return token_data;
}

export const fetch = wrappedFetch;

export default {
  getTokenData,
  logoff,
  login,
  fetch,
};
