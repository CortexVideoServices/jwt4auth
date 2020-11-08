import * as React from 'react';
import { useEffect, useState } from 'react';
import { UserSessionContext } from '@jwt4auth/reactjs';
import jwt4auth from '@jwt4auth/general';

interface Props {
  className: string;
}

function Dashboard({ className }: Props) {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getProtectedMessage = () =>
    jwt4auth
      .fetch('/api/message')
      .then((resp) => {
        if (resp.ok)
          resp.json().then((data) =>
            setMessage(() => {
              setError(null);
              return data.message;
            })
          );
        else
          setError(() => {
            setMessage(null);
            return `Cannot get message; status code ${resp.status}`;
          });
      })
      .catch((err) =>
        setError(() => {
          setMessage(null);
          return `Cannot get message: ${err}`;
        })
      );

  useEffect(() => {
    getProtectedMessage();
    const interval = setInterval(getProtectedMessage, 5 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={className}>
      <UserSessionContext.Consumer>
        {({ user }) => <h2>Current user, {(user && user.display_name) || 'Undefined'}</h2>}
      </UserSessionContext.Consumer>
      <p>
        We will make periodic requests (every five seconds) to the protected URI{' '}
        <span className="text-bold">/api/message</span> in an attempt to retrieve the message. See Browser Development
        Tools for more information.
      </p>
      {message && (
        <p>
          Received message: <span className="text-primary">{message}</span>
        </p>
      )}
      {error && (
        <div className="toast toast-error">
          <button className="btn btn-clear float-right" onClick={() => setError(null)} />
          {error}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
