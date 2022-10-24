import DataTable from 'components/DataTable';
import { ShowHelpPageProvider } from 'hooks/useShowHelpPageState';
import { SnackbarProvider } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { Experiments } from './components/ExperimentTable';
import Tabs, { TabItem } from './components/Tabs';
import { ClientDataProvider } from './hooks/useClientDataState';
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
  stopping: StatusEnum.STOPPING,
} as { [k: string]: StatusEnum };

function AppTabs() {
  const { selectedTab, setSelectedTab } = useSelectedTabState();

  let tabItems: TabItem[] = [];

  if (selectedTab == 0) {
    tabItems = [
      {
        title: 'Experiments',
        content: <Experiments />,
      },
      { title: 'Data', content: <></> },
    ];
  } else if (selectedTab == 1) {
    tabItems = [
      { title: 'Experiments', content: <></> },
      {
        title: 'Data',
        content: <DataTable />,
      },
    ];
  }

  return (
    <ClientDataProvider endpoint="sweeps">
      <ClientDataProvider endpoint="tensorboards">
        <ClientDataProvider endpoint="data">
          <Tabs
            selectedTab={selectedTab}
            onChange={setSelectedTab}
            tabItems={tabItems}
            sxTabs={{ width: '100%', backgroundColor: 'white', paddingX: 2, top: 0, zIndex: 1000 }}
          />
        </ClientDataProvider>
      </ClientDataProvider>
    </ClientDataProvider>
  );
}

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SnackbarProvider>
            <ShowHelpPageProvider>
              <SelectedTabProvider>
                <AppTabs />
              </SelectedTabProvider>
            </ShowHelpPageProvider>
          </SnackbarProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
