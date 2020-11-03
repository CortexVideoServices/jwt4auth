import * as React from 'react';
import { Dispatch, ReactNode, SetStateAction } from 'react';

import * as jwt4auth from '@jwt4auth/javascript';
import { TokenData } from '@jwt4auth/javascript';

// Interface of user session data
interface UserData extends TokenData {
  authenticated: boolean;
}

export type LoginFunction = (username: string, password: string) => Promise<boolean>;
export type LogoffFunction = () => Promise<void>;

// Interface of user session context
interface UserSessionContextProps {
  user: UserData;
  doLogin: LoginFunction;
  doLogoff: LogoffFunction;
}

// Interface of props of user session component
interface UserSessionProps {
  children: ReactNode | ((props: UserSessionContextProps) => ReactNode);
}

// Unauthenticated user
const unauthenticated: UserData = { authenticated: false };

/// User session context
export const UserSessionContext = React.createContext<UserSessionContextProps>({
  user: unauthenticated,
  doLogin: async () => false,
  doLogoff: async () => undefined,
});

// Updates user data
async function updateUserData(setUserData: Dispatch<SetStateAction<UserData>>) {
  const tokenData = await jwt4auth.getTokenData();
  setUserData((prevState) => {
    const newState = tokenData !== null ? { ...tokenData, authenticated: true } : unauthenticated;
    if (prevState.authenticated) return Object.assign(prevState, newState);
    return newState;
  });
}

// Login function
async function login(username: string, password: string, setUserData: Dispatch<SetStateAction<UserData>>) {
  const result = await jwt4auth.login(username, password, () => setUserData(unauthenticated));
  if (result) await updateUserData(setUserData);
  return result;
}

// Logoff function
async function logoff(setUserData: Dispatch<SetStateAction<UserData>>) {
  try {
    await jwt4auth.logoff();
  } finally {
    setUserData(unauthenticated);
  }
}

/// User session component
export function UserSession({ children }: UserSessionProps) {
  const [user, setUserData] = React.useState<UserData>(unauthenticated);
  React.useEffect(() => {
    updateUserData(setUserData).catch(console.log);
  }, []);

  const doLogin: LoginFunction = async (username, password) => login(username, password, setUserData);
  const doLogoff: LogoffFunction = async () => logoff(setUserData);

  return (
    <UserSessionContext.Provider value={{ user, doLogin, doLogoff }}>
      {typeof children === 'function' ? children({ user, doLogin, doLogoff }) : children}
    </UserSessionContext.Provider>
  );
}

export default UserSession;
