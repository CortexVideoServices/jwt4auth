import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { UserSession } from '../src';

describe('it', () => {
  it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<UserSession />, div);
    ReactDOM.unmountComponentAtNode(div);
  });
});
