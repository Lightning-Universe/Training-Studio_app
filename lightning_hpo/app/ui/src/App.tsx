import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { Stack, Typography } from '@mui/material';
import { IconButton, Link, SnackbarProvider, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { Sweeps } from './components/SweepTable';
import Tabs, { TabItem } from './components/Tabs';
import { NotebookConfig } from './generated';
import useClientDataState, { ClientDataProvider } from './hooks/useClientDataState';
import useSelectedTabState, { SelectedTabProvider } from './hooks/useSelectedTabState';

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

function Notebooks() {
  const notebooks = useClientDataState('notebooks') as NotebookConfig[];

  const header = ['Status', 'Name', 'Cloud compute', 'URL', 'More'];

  const rows = notebooks.map(notebook => [
    <Status status={notebook.status ? statusToEnum[notebook.status] : StatusEnum.NOT_STARTED} />,
    notebook.name,
    notebook.cloud_compute,
    <Link href={notebook.url} target="_blank" underline="hover">
      <Stack direction="row" alignItems="center" spacing={0.5}>
        <OpenInNewIcon sx={{ fontSize: 20 }} />
        <Typography variant="subtitle2">Open</Typography>
      </Stack>
    </Link>,
    <IconButton id={notebook.name + '-button'}>
      <MoreHorizIcon sx={{ fontSize: 16 }} />
    </IconButton>,
  ]);

  return <Table header={header} rows={rows} />;
}

function AppTabs() {
  const { selectedTab, setSelectedTab } = useSelectedTabState();

  let tabItems: TabItem[] = [];

  if (selectedTab == 0) {
    tabItems = [
      {
        title: 'Notebooks',
        content: (
          <ClientDataProvider endpoint="notebooks">
            <Notebooks />
          </ClientDataProvider>
        ),
      },
      { title: 'Sweeps & Trials', content: <></> },
    ];
  } else if (selectedTab == 1) {
    tabItems = [
      { title: 'Notebooks', content: <></> },
      {
        title: 'Sweeps & Trials',
        content: (
          <ClientDataProvider endpoint="sweeps">
            <ClientDataProvider endpoint="tensorboards">
              <Sweeps />
            </ClientDataProvider>
          </ClientDataProvider>
        ),
      },
    ];
  }

  return (
    <Tabs
      selectedTab={selectedTab}
      onChange={setSelectedTab}
      tabItems={tabItems}
      sxTabs={{ width: '100%', backgroundColor: 'white', paddingX: 2, top: 0, zIndex: 1000 }}
    />
  );
}

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SnackbarProvider>
            <SelectedTabProvider>
              <AppTabs />
            </SelectedTabProvider>
          </SnackbarProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
