import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import { IconButton, Link, SnackbarProvider, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { Sweeps } from './components/SweepTable';
import TableContainer from './components/TableContainer';
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

  const header = ['Name', 'Stage', 'URL', 'More'];

  const rows = notebooks.map(notebook => [
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
      sxContent={{ paddingTop: 0, paddingBottom: 6, marginTop: '48px' }}
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
