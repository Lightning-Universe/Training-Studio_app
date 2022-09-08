import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import { IconButton, Link, SnackbarProvider, Stack, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { useEffect, useMemo, useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { Sweeps } from './components/SweepTable';
import TableContainer from './components/TableContainer';
import { AppClient, NotebookConfig, SweepConfig, TensorboardConfig } from './generated';

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
  const header = ['Name', 'Status', 'URL', 'More'];

  const rows = props.notebooks.map(notebook => [
    notebook.name,
    <Status status={notebook.status ? statusToEnum[notebook.status] : StatusEnum.NOT_STARTED} />,
    <Link href={notebook.url} target="_blank">
      Click Me
    </Link>,
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
  const [tensorboards, setTensorboards] = useState<TensorboardConfig[]>([]);

  useEffect(() => {
    appClient.appClientCommand
      .showNotebooksCommandShowNotebooksPost()
      .then(data => setNotebooks(data as NotebookConfig[]));

    appClient.appClientCommand.showSweepsCommandShowSweepsPost().then(data => setSweeps(data as SweepConfig[]));

    appClient.appCommand
      .showTensorboardsCommandShowTensorboardsPost()
      .then(data => setTensorboards(data as TensorboardConfig[]));

    const interval = setInterval(() => {
      appClient.appClientCommand
        .showNotebooksCommandShowNotebooksPost()
        .then(data => setNotebooks(data as NotebookConfig[]));

      appClient.appClientCommand.showSweepsCommandShowSweepsPost().then(data => setSweeps(data as SweepConfig[]));

      appClient.appCommand
        .showTensorboardsCommandShowTensorboardsPost()
        .then(data => setTensorboards(data as TensorboardConfig[]));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Stack>
      <Notebooks notebooks={notebooks} />
      <Sweeps sweeps={sweeps} tensorboards={tensorboards} />
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
