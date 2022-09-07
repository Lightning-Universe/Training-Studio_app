import { SnackbarProvider, Stack } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import React, { useEffect, useMemo, useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { AppClient, NotebookConfig } from './generated';

const queryClient = new QueryClient();

function Main() {
  const appClient = useMemo(
    () =>
      new AppClient({
        BASE:
          window.location != window.parent.location
            ? document.referrer.replace(/\/$/, '')
            : document.location.href.replace(/\/$/, ''),
      }),
    [],
  );

  const [notebooks, setNotebooks] = useState<NotebookConfig[]>([]);

  useEffect(() => {
    appClient.appClientCommand
      .showNotebooksCommandShowNotebooksPost()
      .then(data => setNotebooks(data as NotebookConfig[]));
    const interval = setInterval(() => {
      appClient.appClientCommand
        .showNotebooksCommandShowNotebooksPost()
        .then(data => setNotebooks(data as NotebookConfig[]));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <Stack order="column">{JSON.stringify(notebooks)}</Stack>;
}

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SnackbarProvider>
            <Main />
          </SnackbarProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
