export type OnSession = (userData: UserData | void) => void;
export type DoLogin = (username: string, password: string) => Promise<boolean>;
export type DoLogoff = () => Promise<void>;

/**
 * User data
 */
export interface UserData {
  [index: string]: any;
}

/**
 * Authentication and authorization subject domain settings
 */
export interface AuthDomainSettings {
  onSession: OnSession;
}

/**
 * Authentication and authorization subject domain
 */
namespace AuthDomain {
  let user_data: UserData | void;
  let refresh_token: string | void;
  let on_session: OnSession = () => undefined;

  function start_session(user_data_: UserData, refresh_token_: string) {
    user_data = user_data_;
    refresh_token = refresh_token_;
    on_session(user_data);
  }

  function end_session() {
    user_data = undefined;
    refresh_token = undefined;
    on_session(user_data);
  }

  /**
   * Setups internal state of a domain
   * @param onSession
   */
  export function setup({ onSession = on_session }: AuthDomainSettings): void {
    on_session = onSession;
  }

  /**
   * Tries to login and create a new user session
   * @param username Username (email, phone, login name or other unique user ID)
   * @param password Password
   */
  export async function login(username: string, password: string): Promise<boolean> {
    if (await getUserData()) return true;
    // ToDo: Need to be implemented
    if (password === '123456') {
      start_session({ username }, 'refresh-token');
      return true;
    }
    return false;
  }

  /**
   * Closes (logs out) the current user session.
   */
  export async function logoff(): Promise<void> {
    if (refresh_token) {
      // ToDo: Need to be implemented
      end_session();
    }
  }

  /**
   * Returns the latest user data.
   * @return {UserData | void}
   */
  export async function getUserData(): Promise<UserData | void> {
    // ToDo: Need to be implemented
    return user_data;
  }
}

export default AuthDomain;
