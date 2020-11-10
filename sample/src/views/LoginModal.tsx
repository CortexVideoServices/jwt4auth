import React, { useState } from 'react';
import { useHistory } from 'react-router';
import { Switch, Route, Redirect } from 'react-router-dom';
import { FastField, Form, Formik } from 'formik';
import { UserSessionContext } from '@jwt4auth/reactjs';

function LoginModal() {
  const history = useHistory();
  const [error, setError] = useState<string | null>(null);

  const closeModal = () => {
    setError(null);
    history.push('/');
  };

  return (
    <Switch>
      <Route path="/login">
        <UserSessionContext.Consumer>
          {({ user, login }) =>
            user ? (
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
                      if (await login(username, password)) closeModal();
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
                          OK
                        </button>
                      </div>
                    </Form>
                  </Formik>
                </div>
              </div>
            )
          }
        </UserSessionContext.Consumer>
      </Route>
    </Switch>
  );
}

export default LoginModal;
