import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
// Anek Devanagari carries both Devanagari and Latin, with the condensed widths the chips use.
import '@fontsource-variable/anek-devanagari/wdth.css';
import './styles.css';
import App from './App';

const root = document.getElementById('root');
if (!root) throw new Error('index.html has no #root element');

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
