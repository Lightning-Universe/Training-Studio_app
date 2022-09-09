import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { Typography } from '@mui/material';
import { Link, SnackbarProvider, Stack, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import MoreMenu from './components/MoreMenu';
import StartStopMenuItem from './components/StartStopMenuItem';
import { Sweeps } from './components/SweepTable';
import Tabs, { TabItem } from './components/Tabs';
import UserGuide, { UserGuideBody, UserGuideComment } from './components/UserGuide';
import { NotebookConfig } from './generated';
import useClientDataState, { appClient, ClientDataProvider } from './hooks/useClientDataState';
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

  if (notebooks.length == 0) {
    return (
      <UserGuide title="Want to start a notebook?" subtitle="Use the commands below">
        <UserGuideComment>Connect to the app</UserGuideComment>
        <UserGuideBody>{'lightning connect {APP_ID_OR_NAME_OR_LOCALHOST} --yes'}</UserGuideBody>
        <UserGuideComment>Run a notebook</UserGuideComment>
        <UserGuideBody>lightning run notebook my_notebook</UserGuideBody>
      </UserGuide>
    );
  }

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
    <MoreMenu
      id={notebook.name}
      items={[
        StartStopMenuItem(
          notebook.status || '',
          () => {
            appClient.appClientCommand.runNotebookCommandRunNotebookPost({
              id: notebook.id,
              name: notebook.name,
              requirements: notebook.requirements,
              cloud_compute: notebook.cloud_compute,
            });
          },
          () => {
            appClient.appClientCommand.stopNotebookCommandStopNotebookPost({ name: notebook.name });
          },
        ),
      ]}
    />,
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
