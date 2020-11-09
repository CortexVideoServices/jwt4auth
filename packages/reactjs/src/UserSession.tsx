import * as React from 'react';
import { UserData } from '@jwt4auth/general';
import { ReactNode, useEffect } from 'react';

/// User session
interface Session {
  user?: UserData;
}

/// User session context
export const UserSessionContext = React.createContext<Session>({});

interface Props {
  children: ReactNode | ((props: Session) => ReactNode);
}

/// User session component
export function UserSession({ children }: Props) {
  const [user, setUser] = React.useState<UserData>();
  useEffect(() => {
    setUser(undefined);
  }, []);
  return (
    <UserSessionContext.Provider value={{ user }}>
      {typeof children === 'function' ? children({ user }) : children}
    </UserSessionContext.Provider>
  );
}

export default UserSession;
