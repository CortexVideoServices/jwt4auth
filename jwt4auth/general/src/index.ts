/**
 * User data
 */
export interface UserData {
  [index: string]: any;
}

/**
 * Token data
 */
export interface TokenData {
  username: string;
  user_data?: UserData;
  [index: string]: any;
}

export type OnSessionAbort = () => void;

interface AuthInitProps {
  uriPrefix: string;
  refreshTokenKey: string;
  onSessionAbort: OnSessionAbort;
}

/**
 * Authentication and authorisation domain.
 */
namespace Auth {
  let uri_prefix: string = '/auth';
  let refresh_token_key: string = 'refresh_token';
  let on_session_abort: OnSessionAbort = () => undefined;
  let refresh_token: string | null = localStorage.getItem(refresh_token_key);
  let token_data: TokenData | null = null;

  /**
   * Setups the auth domain
   * @param {string} uriPrefix URI prefix for the auth domain requests to the backend.
   * @param {string} refreshTokenKey The name of the key under which the refresh token is stored in local storage.
   * @param {OnSessionAbort} onSessionAbort If specified, called after an interruption or normal end of the user's session.
   */
  export function setup({
    uriPrefix = uri_prefix,
    refreshTokenKey = refresh_token_key,
    onSessionAbort = on_session_abort,
  }: Partial<AuthInitProps>) {
    uri_prefix = uriPrefix;
    refresh_token_key = refreshTokenKey;
    on_session_abort = onSessionAbort;
  }

  /**
   * Tries to enter a new user session
   * @param {string} username EMail, phone or other login name.
   * @param {string} password User password.
   * @return {boolean} True if the user's session has been established.
   */
  export async function login(username: string, password: string): Promise<boolean> {
    if (refresh_token) return true;
    const resp = await fetch(`${uri_prefix}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data && data.token_data && data.token_data.username && data.refresh_token) {
        localStorage.setItem(refresh_token_key, data.refresh_token);
        refresh_token = data.refresh_token;
        token_data = data.token_data;
        return true;
      }
    }
    return false;
  }

  /**
   * Refreshes user session (refreshes session tokens).
   * @return {boolean} True if the user's session has been refreshed.
   */
  export async function refresh(): Promise<boolean> {
    if (refresh_token) {
      const resp = await fetch(`${uri_prefix}/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token }),
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.token_data && data.token_data.username && data.refresh_token) {
          localStorage.setItem(refresh_token_key, data.refresh_token);
          refresh_token = data.refresh_token;
          token_data = data.token_data;
          return true;
        }
      }
      localStorage.removeItem(refresh_token_key);
      refresh_token = null;
      token_data = null;
    }
    return false;
  }

  /**
   * Closes user session
   */
  export async function logoff(): Promise<void> {
    if (refresh_token) {
      try {
        await fetch(`${uri_prefix}/logoff`);
      } finally {
        localStorage.removeItem(refresh_token_key);
        refresh_token = null;
        token_data = null;
      }
    }
  }

  /**
   * Returns user data
   * @return {UserData | null} User data if user's session is established or null.
   */
  export async function getUserData(): Promise<UserData | null> {
    if (refresh_token) {
      if (token_data === null || ('exp' in token_data && token_data.exp * 1000 > Date.now())) await refresh();
      if (token_data) {
        return token_data.user_data || { username: token_data.username };
      }
    }
    return null;
  }

  /**
   * Intercepted `fetch`. In case of a 401 error, it tries to update the access token and retry the request.
   * @param input
   * @param init
   */
  export async function fetch(input: RequestInfo, init?: RequestInit): Promise<Response> {
    const _init = init || ({} as RequestInit);
    _init.credentials = refresh_token ? 'same-origin' : 'omit';
    let resp = await window.fetch(input, _init);
    if (resp.status === 401 && _init.credentials !== 'omit') {
      if (await refresh()) {
        resp = await window.fetch(input, _init);
      }
    }
    return resp;
  }
}

export default Auth;
