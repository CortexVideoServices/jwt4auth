import * as React from 'react';
import auth, { DoLogin, DoLogoff, OnSession, UserData } from '@jwt4auth/general';
import { ReactNode, useEffect } from 'react';
import AuthDomain from '@jwt4auth/general';
import refresh = AuthDomain.refresh;

/// User session
interface Session {
  user?: UserData;
  login: DoLogin;
  logoff: DoLogoff;
}

/// User session context
export const UserSessionContext = React.createContext<Session>({
  login: async () => false,
  logoff: async () => undefined,
});

interface Props {
  children: ReactNode | ((props: Session) => ReactNode);
}

/// User session component
export function UserSession({ children }: Props) {
  const [user, setUser] = React.useState<UserData>();
  const listener: OnSession = (data) => {
    setUser((_) => data);
  };
  useEffect(() => {
    auth.addSessionListener(listener);
    refresh();
    return () => auth.removeListener(listener);
  }, []);

  const login: DoLogin = async (username, password) => {
    return await auth.login(username, password);
  };
  const logoff: DoLogoff = async () => {
    await auth.logoff();
  };

  return (
    <UserSessionContext.Provider value={{ user, login, logoff }}>
      {typeof children === 'function' ? children({ user, login, logoff }) : children}
    </UserSessionContext.Provider>
  );
}

export default UserSession;
