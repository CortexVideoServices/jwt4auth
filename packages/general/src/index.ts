export type OnSession = (userData: UserData | void) => void;
export type DoLogin = (username: string, password: string) => Promise<boolean>;
export type DoLogoff = () => Promise<void>;

/**
 * User data
 */
export interface UserData {
  [index: string]: any;
}

interface SessionData {
  user_data: UserData;
  refresh_token: string;
}

/**
 * Authentication and authorization subject domain settings
 */
export interface AuthDomainSettings {
  uriPrefix?: string;
  refreshTokenKey?: string;
}

/**
 * Authentication and authorization subject domain
 */
namespace AuthDomain {
  let uri_prefix: string = '';
  let refresh_token_key: string = 'refresh_token';
  let on_session_listener = new Set<OnSession>();

  let user_data: UserData | void;
  let refresh_token: string | null = localStorage.getItem(refresh_token_key);

  function start_session(data: SessionData) {
    user_data = data.user_data;
    refresh_token = data.refresh_token;
    localStorage.setItem(refresh_token_key, refresh_token);
    for (const on_session of Array.from(on_session_listener)) on_session(user_data);
  }

  function end_session() {
    user_data = undefined;
    refresh_token = null;
    localStorage.removeItem(refresh_token_key);
    for (const on_session of Array.from(on_session_listener)) on_session(user_data);
  }

  /**
   * Setups internal state of a domain
   * @param {string} uriPrefix URI prefix for the auth domain requests to the backend.
   * @param {string} refreshTokenKey The name of the key under which the refresh token is stored in local storage.
   */
  export function setup({ uriPrefix, refreshTokenKey = refresh_token_key }: AuthDomainSettings): void {
    if (uriPrefix) uri_prefix = uriPrefix;
    if (refresh_token_key !== refreshTokenKey) {
      refresh_token_key = refreshTokenKey;
      refresh_token = localStorage.getItem(refresh_token_key);
    }
  }

  /**
   * Adds session changing listener
   * @param onSession {OnSession} handler called when session state changed
   */
  export function addSessionListener(onSession: OnSession) {
    on_session_listener.add(onSession);
  }

  /**
   * Removes session changing listener
   * @param onSession {OnSession} handler to remove
   */
  export function removeListener(onSession: OnSession) {
    on_session_listener.delete(onSession);
  }

  /**
   * Tries to login and create a new user session
   * @param username {string} Username (email, phone, login name or other unique user ID)
   * @param password {string} Password
   */
  export async function login(username: string, password: string): Promise<boolean> {
    if (await getUserData()) return true;
    const resp = await fetch(`${uri_prefix}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data && data.user_data && data.refresh_token) {
        start_session(data as SessionData);
        return true;
      }
    }
    return false;
  }

  /**
   * Refreshes user session (refreshes session tokens).
   * @return {boolean} True if the user's session has been refreshed.
   * @todo Make a lock to avoid concurrent requests.
   */
  export async function refresh(): Promise<boolean> {
    if (refresh_token) {
      const resp = await fetch(`${uri_prefix}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token }),
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.user_data && data.refresh_token) {
          start_session(data as SessionData);
          return true;
        }
      }
    }
    end_session();
    return false;
  }

  /**
   * Closes (logs out) the current user session.
   */
  export async function logoff(): Promise<void> {
    if (refresh_token) {
      try {
        await fetch(`${uri_prefix}/auth/logoff`);
      } finally {
        end_session();
      }
    }
  }

  /**
   * Returns the latest user data.
   * @return {UserData | void}
   */
  export async function getUserData(force: boolean = false): Promise<UserData | void> {
    if (force) await refresh();
    return user_data;
  }

  /**
   * Intercepted `fetch`. In case of a 401 error, it tries to update the access token and retry the request.
   * @param input
   * @param init
   */
  export async function fetch(input: RequestInfo, init?: RequestInit): Promise<Response> {
    const _init = init || ({} as RequestInit);
    const is_refresh_request = () => (typeof input === 'string' ? input : input.url).endsWith('/refresh');
    const is_login_request = () => (typeof input === 'string' ? input : input.url).endsWith('/login');
    if (refresh_token === null && !is_login_request()) _init.credentials = 'omit';
    let resp = await window.fetch(input, _init);
    if (resp.status === 401 && _init.credentials !== 'omit' && !is_refresh_request()) {
      if (await refresh()) {
        resp = await window.fetch(input, _init);
      }
    }
    return resp;
  }
}

export default AuthDomain;
