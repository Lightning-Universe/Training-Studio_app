import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import StopCircleIcon from '@mui/icons-material/StopCircle';
import { SnackbarProvider, Stack, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import React, { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import MoreMenu from './components/MoreMenu';
import TableContainer from './components/TableContainer';
import { AppClient, NotebookConfig } from './generated';

const queryClient = new QueryClient();

const appClient = new AppClient({
  BASE:
    window.location != window.parent.location
      ? document.referrer.replace(/\/$/, '')
      : document.location.href.replace(/\/$/, ''),
});

const statusToEnum = {
  not_started: StatusEnum.NOT_STARTED,
  pending: StatusEnum.PENDING,
  running: StatusEnum.RUNNING,
  pruned: StatusEnum.DELETED,
  succeeded: StatusEnum.SUCCEEDED,
  failed: StatusEnum.FAILED,
  stopped: StatusEnum.STOPPED,
} as { [k: string]: StatusEnum };

function Notebooks(props: { notebooks: NotebookConfig[] }) {
  const header = ['Name', 'Status', 'More'];

  const rows = props.notebooks.map(notebook => [
    notebook.name,
    <Status status={notebook.status ? statusToEnum[notebook.status] : StatusEnum.NOT_STARTED} />,
    <MoreMenu
      id={notebook.name}
      items={[
        {
          label: notebook.status === 'stopped' ? 'Start' : 'Stop',
          icon:
            notebook.status === 'stopped' ? (
              <PlayCircleIcon sx={{ fontSize: 16 }} />
            ) : (
              <StopCircleIcon sx={{ fontSize: 16 }} />
            ),
          onClick: () => {
            if (notebook.status === 'stopped') {
              console.log('starting');
              appClient.appClientCommand.runNotebookCommandRunNotebookPost({
                id: notebook.id,
                name: notebook.name,
                requirements: notebook.requirements,
                cloud_compute: notebook.cloud_compute,
              });
            } else {
              console.log('stopping');
              appClient.appClientCommand.stopNotebookCommandStopNotebookPost({ name: notebook.name });
            }
          },
        },
      ]}
    />,
  ]);

  return (
    <TableContainer header="Notebooks">
      <Table header={header} rows={rows} />
    </TableContainer>
  );
}

function Main() {
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

  return (
    <Stack order="column">
      <Notebooks notebooks={notebooks} />
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
