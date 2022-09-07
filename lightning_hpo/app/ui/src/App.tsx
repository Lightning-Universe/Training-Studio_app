import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import { IconButton, SnackbarProvider, Stack, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { useEffect, useMemo, useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import TableContainer from './components/TableContainer';
import { AppClient, NotebookConfig, SweepConfig } from './generated';

const queryClient = new QueryClient();

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
    <IconButton id={notebook.name + '-button'}>
      <MoreHorizIcon sx={{ fontSize: 16 }} />
    </IconButton>,
  ]);

  return (
    <TableContainer header="Notebooks">
      <Table header={header} rows={rows} />
    </TableContainer>
  );
}

function Sweeps(props: { sweeps: SweepConfig[] }) {
  const header = ['Name', 'Status', 'More'];

  const rows = props.sweeps.map(sweep => [
    sweep.id,
    <Status status={sweep.status ? statusToEnum[sweep.status] : StatusEnum.NOT_STARTED} />,
    <IconButton id={sweep.id + '-button'}>
      <MoreHorizIcon sx={{ fontSize: 16 }} />
    </IconButton>,
  ]);

  return (
    <TableContainer header="Sweeps">
      <Table header={header} rows={rows} />
    </TableContainer>
  );
}

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
      <Notebooks notebooks={notebooks} />
      <Sweeps sweeps={sweeps} />
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
