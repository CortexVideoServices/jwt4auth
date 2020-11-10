import React from 'react';
import { UserSession, UserSessionContext } from '@jwt4auth/reactjs';
import { Link } from 'react-router-dom';
import 'spectre.css';
import Dashboard from './views/Dashboard';
import LoginModal from './views/LoginModal';

function App() {
  return (
    <UserSession>
      <LoginModal />
      <div className="container grid-lg p-1">
        <header className="navbar">
          <section className="navbar-section" />
          <UserSessionContext.Consumer>
            {({ user, logoff }) => (
              <section className="navbar-section">
                {!user ? (
                  <Link className="btn btn-link" to="/login">
                    Login
                  </Link>
                ) : (
                  <Link className="btn btn-link" to="/" onClick={logoff}>
                    Logoff
                  </Link>
                )}
              </section>
            )}
          </UserSessionContext.Consumer>
        </header>
        <div className="container f">
          <div className="columns">
            <div className="column hero-body bg-gray p-2 m-2">
              <h2>Hello, All!</h2>
              <p>
                This demo application will show you a working example of using the{' '}
                <span className="text-bold">jwt4auth</span> library in a React application. Hopefully this helps you get
                started using <span className="text-bold">jwt4auth</span> in your own application.
              </p>
              <p>Please login:</p>
              <ul>
                <li>Use any username</li>
                <li>Use password: 123456</li>
              </ul>
            </div>
            <div className="column hero-body bg-gray p-2 m-2">
              <Dashboard />
            </div>
          </div>
        </div>
      </div>
    </UserSession>
  );
}

export default App;
