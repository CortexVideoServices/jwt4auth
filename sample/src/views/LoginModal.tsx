import * as React from 'react';
import { useContext, useState } from 'react';
import { Formik, Form, FastField } from 'formik';
import { Redirect, Route, Switch, useHistory } from 'react-router';
import { UserSessionContext } from '@jwt4auth/reactjs';

function LoginModal() {
  const history = useHistory();
  const session = useContext(UserSessionContext);
  const [error, setError] = useState<string | null>(null);

  const closeModal = () => {
    setError(null);
    history.push('/');
  };

  return (
    <Switch>
      <Route path="/login">
        {session.user ? (
          <Redirect to="/" />
        ) : (
          <div className="modal active" id="modal-id">
            <div onClick={closeModal} className="modal-overlay" aria-label="Close" />
            <div className="modal-container">
              <div className="modal-header">
                <div onClick={closeModal} className="btn btn-clear float-right" aria-label="Close" />
                <div className="modal-title h5">Login</div>
              </div>
              <Formik
                initialValues={{ username: '', password: '' }}
                onSubmit={async ({ username, password }) => {
                  if (await session.login(username, password)) closeModal();
                  else setError('Incorrect username or password');
                }}
              >
                <Form>
                  <div className="modal-body">
                    <div className="content">
                      <div className="form-group">
                        <label className="form-label" htmlFor="login-username">
                          Username
                        </label>
                        <FastField className="form-input" id="login-username" name="username" />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="login-password">
                          Password
                        </label>
                        <FastField className="form-input" id="login-password" type="password" name="password" />
                      </div>
                    </div>
                  </div>
                  {error && (
                    <div className="modal-body">
                      <div className="toast toast-error">
                        <button className="btn btn-clear float-right" onClick={() => setError(null)} />
                        {error}
                      </div>
                    </div>
                  )}
                  <div className="modal-footer">
                    <button type="submit" className="btn btn-primary">
                      Enter
                    </button>
                  </div>
                </Form>
              </Formik>
            </div>
          </div>
        )}
      </Route>
    </Switch>
  );
}

export default LoginModal;
