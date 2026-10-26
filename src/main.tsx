import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { App } from './app/App';
import { useStore } from './state/store';

// test hook: expose the store for end-to-end tests
(window as unknown as { __c7: typeof useStore }).__c7 = useStore;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
