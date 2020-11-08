import * as React from 'react';
import { ReactNode, useEffect } from 'react';
import jwt4auth, { UserData } from '@jwt4auth/general';

export type LoginFunction = (username: string, password: string) => Promise<boolean>;
export type RefreshFunction = () => Promise<boolean>;
export type LogoffFunction = () => Promise<void>;

/// User session
interface Session {
  user?: UserData;
  login: LoginFunction;
  refresh: RefreshFunction;
  logoff: LogoffFunction;
}

/// User session context
export const UserSessionContext = React.createContext<Session>({
  login: async () => false,
  refresh: async () => false,
  logoff: async () => undefined,
});

interface Props {
  children: ReactNode | ((props: Session) => ReactNode);
}

/// User session component
export function UserSession({ children }: Props) {
  const [user, setUser] = React.useState<UserData>();
  useEffect(() => {
    jwt4auth.setup({ onSessionAbort: () => setUser(undefined) });
    jwt4auth.getUserData().then((user_data) => {
      setUser(user_data || undefined);
    });
  }, []);

  const doLogin: LoginFunction = async (username, password) => {
    if (!user) {
      let user_data: UserData | null = null;
      if (await jwt4auth.login(username, password)) {
        user_data = await jwt4auth.getUserData();
      }
      setUser(user_data || undefined);
      return user_data !== null;
    }
    return true;
  };

  const doRefresh: RefreshFunction = async () => {
    const user_data = await jwt4auth.getUserData();
    setUser(user_data || undefined);
    return user_data !== null;
  };

  const doLogoff: LogoffFunction = async () => {
    if (user) {
      try {
        await jwt4auth.logoff();
      } finally {
        setUser(undefined);
      }
    }
  };

  return (
    <UserSessionContext.Provider value={{ user, login: doLogin, refresh: doRefresh, logoff: doLogoff }}>
      {typeof children === 'function'
        ? children({ user, login: doLogin, refresh: doRefresh, logoff: doLogoff })
        : children}
    </UserSessionContext.Provider>
  );
}
