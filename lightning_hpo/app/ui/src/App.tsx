import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { Typography } from '@mui/material';
import { ShowHelpPageProvider } from 'hooks/useShowHelpPageState';
import { Link, SnackbarProvider, Stack, Table } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { Experiments } from './components/ExperimentTable';
import MoreMenu from './components/MoreMenu';
import StartStopMenuItem from './components/StartStopMenuItem';
import Tabs, { TabItem } from './components/Tabs';
import UserGuide, { UserGuideBody, UserGuideComment } from './components/UserGuide';
import { NotebookConfig } from './generated';
import useClientDataState, { appClient, ClientDataProvider } from './hooks/useClientDataState';
import useSelectedTabState, { SelectedTabProvider } from './hooks/useSelectedTabState';
import { formatDurationFrom, getAppId } from './utilities';

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

function Notebooks() {
  const notebooks = useClientDataState('notebooks') as NotebookConfig[];
  const appId = getAppId();
  const enableClipBoard = appId == 'localhost' ? false : true;

  if (notebooks.length == 0) {
    return (
      <UserGuide
        title="Want to start a notebook?"
        subtitle="Use the commands below in your terminal or click on 'New'">
        <UserGuideComment>Connect to the app</UserGuideComment>
        <UserGuideBody enableClipBoard={enableClipBoard}>{`lightning connect ${appId} --yes`}</UserGuideBody>
        <UserGuideComment>Run a notebook</UserGuideComment>
        <UserGuideBody enableClipBoard={enableClipBoard}>lightning run notebook --name=my_notebook</UserGuideBody>
      </UserGuide>
    );
  }

  const header = ['Status', 'Name', 'Cloud compute', 'Run time', 'URL', 'More'];

  const rows = notebooks.map(notebook => {
    const link = (
      <Link href={notebook.url} target="_blank" underline="hover">
        <Stack direction="row" alignItems="center" spacing={0.5}>
          <OpenInNewIcon sx={{ fontSize: 20 }} />
          <Typography variant="subtitle2">Open</Typography>
        </Stack>
      </Link>
    );

    return [
      <Status status={notebook.stage ? statusToEnum[notebook.stage] : StatusEnum.NOT_STARTED} />,
      notebook.notebook_name,
      notebook.cloud_compute,
      notebook.stage == 'running' ? formatDurationFrom(notebook.start_time || 0) : '-',
      notebook.url ? link : '-',
      <MoreMenu
        id={notebook.notebook_name}
        items={[
          StartStopMenuItem(
            notebook.stage || '',
            () => {
              appClient.appClientCommand.runNotebookCommandRunNotebookPost({
                notebook_name: notebook.notebook_name,
                requirements: notebook.requirements,
                cloud_compute: notebook.cloud_compute,
              });
            },
            () => {
              appClient.appClientCommand.stopNotebookCommandStopNotebookPost({
                notebook_name: notebook.notebook_name,
              });
            },
          ),
        ]}
      />,
    ];
  });

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
      { title: 'Experiments', content: <></> },
    ];
  } else if (selectedTab == 1) {
    tabItems = [
      { title: 'Notebooks', content: <></> },
      {
        title: 'Experiments',
        content: (
          <ClientDataProvider endpoint="sweeps">
            <ClientDataProvider endpoint="tensorboards">
              <Experiments />
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

function AppTabsExperiments() {
  const { selectedTab, setSelectedTab } = useSelectedTabState();

  let tabItems: TabItem[] = [];

  tabItems = [
    {
      title: 'Experiments',
      content: (
        <ClientDataProvider endpoint="sweeps">
          <ClientDataProvider endpoint="tensorboards">
            <Experiments />
          </ClientDataProvider>
        </ClientDataProvider>
      ),
    },
  ];

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
            <ShowHelpPageProvider>
              <SelectedTabProvider>
                <AppTabsExperiments />
              </SelectedTabProvider>
            </ShowHelpPageProvider>
          </SnackbarProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
