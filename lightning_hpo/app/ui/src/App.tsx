import { SnackbarProvider, Stack } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import React, { useEffect, useMemo, useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { AppClient, NotebookConfig, SweepConfig } from './generated';

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
  const [sweeps, setSweeps] = useState<SweepConfig[]>([]);

  useEffect(() => {
    appClient.appClientCommand
      .showNotebooksCommandShowNotebooksPost()
      .then(data => setNotebooks(data as NotebookConfig[]));

    appClient.appClientCommand.showSweepsCommandShowSweepsPost().then(data => setSweeps(data as SweepConfig[]));

    const interval = setInterval(() => {
      appClient.appClientCommand
        .showNotebooksCommandShowNotebooksPost()
        .then(data => setNotebooks(data as NotebookConfig[]));

      appClient.appClientCommand.showSweepsCommandShowSweepsPost().then(data => setSweeps(data as SweepConfig[]));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Stack order="column">
      {JSON.stringify(notebooks)} {JSON.stringify(sweeps)}
    </Stack>
  );
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
