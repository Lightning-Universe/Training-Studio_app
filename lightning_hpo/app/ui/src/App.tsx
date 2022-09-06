import { Typography } from '@mui/material';
import Tabs, { TabItem } from 'components/Tabs';
import { useLightningState } from 'hooks/useLightningState';
import useSelectedTabState, { SelectedTabProvider } from 'hooks/useSelectedTabState';
import { SnackbarProvider, Stack } from 'lightning-ui/src/design-system/components';
import ThemeProvider from 'lightning-ui/src/design-system/theme';
import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';

const queryClient = new QueryClient();

function Home(props: { lightningState: any; updateLightningState: (newState: any) => void }) {
  return (
    <Stack order="column">
      <Typography>IN PROGRESS</Typography>
    </Stack>
  );
}

function AppTabs() {
  const { lightningState, updateLightningState } = useLightningState();
  const { selectedTab, setSelectedTab } = useSelectedTabState();

  const tabItems: TabItem[] = [
    { title: 'Home', content: <Home lightningState={lightningState} updateLightningState={updateLightningState} /> },
  ];

  return (
    <Tabs
      selectedTab={selectedTab}
      onChange={setSelectedTab}
      tabItems={tabItems}
      sxTabs={{ width: '100%', backgroundColor: 'white', paddingX: 2, top: 0, position: 'fixed', zIndex: 1000 }}
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
