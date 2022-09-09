import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import { IconButton, Link, SnackbarProvider, Stack, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { useEffect, useMemo, useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import TableContainer from './components/TableContainer';
import { AppClient, NotebookConfig, SweepConfig, TrialConfig } from './generated';

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
  const header = ['Name', 'Stage', 'URL', 'More'];

  const rows = props.notebooks.map(notebook => [
    notebook.notebook_name,
    <Status status={notebook.state ? statusToEnum[notebook.state] : StatusEnum.NOT_STARTED} />,
    <Link href={notebook.url} target="_blank">
      Click Me
    </Link>,
    <IconButton id={notebook.notebook_name + '-button'}>
      <MoreHorizIcon sx={{ fontSize: 16 }} />
    </IconButton>,
  ]);

  return (
    <TableContainer header="Notebooks">
      <Table header={header} rows={rows} />
    </TableContainer>
  );
}

function TrialToRows(trials: Record<string, TrialConfig>) {
  return Object.entries(trials).map(entry => [
    entry[0],
    <Status status={entry[1].status ? statusToEnum[entry[1].status] : StatusEnum.NOT_STARTED} />,
    String(entry[1].best_model_score),
    ...Object.entries(entry[1].params.params).map(value => String(value[1])),
  ]);
}

function generateTrialHeader(trialHeader: string[], params) {
  const paramsHeader = Object.entries(params).map(entry => entry[0]);
  return trialHeader.concat(paramsHeader);
}

function Sweeps(props: { sweeps: SweepConfig[] }) {
  const sweepHeader = [
    'Name',
    'Status',
    'Number of trials',
    'Number of trials done',
    'Framework',
    'Cloud Compute',
    'Direction',
    'URL',
    'More',
  ];
  const baseTrialHeader = ['Name', 'Status', 'Best Model Score'];

  const rows = props.sweeps.map(sweep => [
    sweep.sweep_id,
    <Status status={sweep.state ? statusToEnum[sweep.state] : StatusEnum.NOT_STARTED} />,
    sweep.n_trials,
    sweep.trials_done,
    sweep.framework,
    sweep.cloud_compute,
    sweep.direction,
    <Link href={sweep.url} target="_blank">
      Click Me
    </Link>,
    <IconButton id={sweep.sweep_id + '-button'}>
      <MoreHorizIcon sx={{ fontSize: 16 }} />
    </IconButton>,
  ]);

  const rowDetails = props.sweeps.map(sweep => (
    <Stack>
      <TableContainer header={'Trials (' + sweep.trials[0].monitor + ')'}>
        <Table
          header={generateTrialHeader(baseTrialHeader, sweep.trials[0].params.params)}
          rows={TrialToRows(sweep.trials)}
        />
      </TableContainer>
    </Stack>
  ));

  return (
    <TableContainer header="Sweeps">
      <Table header={sweepHeader} rows={rows} rowDetails={rowDetails} />
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
    <Stack>
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
