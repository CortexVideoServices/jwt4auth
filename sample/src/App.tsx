import React from 'react';
import { UserSession } from '@jwt4auth/reactjs';

function App() {
  return (
    <UserSession>
      <div className="App">Hello, world!</div>
    </UserSession>
  );
}

export default App;
