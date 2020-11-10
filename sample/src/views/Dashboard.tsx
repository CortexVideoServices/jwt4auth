import React, { useContext, useEffect, useState } from 'react';
import { UserSessionContext } from '@jwt4auth/reactjs';

function Dashboard() {
  const ctx = useContext(UserSessionContext);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getMessage = () =>
    fetch('/api/message')
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
    getMessage();
    const interval = setInterval(getMessage, 5 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <h2>Current user, {ctx.user && ctx.user.username ? ctx.user.username : 'Undefined'}</h2>
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
    </>
  );
}

export default Dashboard;
