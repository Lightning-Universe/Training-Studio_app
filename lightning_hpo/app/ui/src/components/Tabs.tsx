import { Divider, Grid, Typography } from '@mui/material';
import MuiTab from '@mui/material/Tab';
import MuiTabs from '@mui/material/Tabs';
import { Box, SxProps, Theme } from 'lightning-ui/src/design-system/components';
import TabContent from 'lightning-ui/src/design-system/components/tabs/TabContent';
import TabPanel from 'lightning-ui/src/design-system/components/tabs/TabPanel';
import { ReactNode } from 'react';

export type TabItem = {
  title: string;
  content: ReactNode;
};

export type TabsProps = {
  selectedTab: number;
  onChange: (selectedTab: number) => void;
  tabItems: TabItem[];
  variant?: 'text' | 'outlined';
  sxTabs?: SxProps<Theme>;
  sxContent?: SxProps<Theme>;
};

const Tabs = (props: TabsProps) => {
  return (
    <Box sx={{ overflowX: 'hidden' }}>
      <Grid container spacing={1}>
        <Grid item xs={12} sm="auto">
          <Box sx={{ marginX: '14px', marginY: '8px' }}>
            <Typography variant="h6">Training Studio</Typography>
          </Box>
        </Grid>
        <Grid item xs={12} sm>
          <MuiTabs
            value={props.selectedTab}
            onChange={(e, value) => props.onChange(value)}
            variant={'scrollable'}
            sx={props.sxTabs}>
            {props.tabItems.map((tabItem: any, index) => (
              // @ts-ignore
              <MuiTab key={tabItem.title} label={tabItem.title} variant={props.variant} />
            ))}
          </MuiTabs>
        </Grid>
      </Grid>
      <Divider />
      <Box paddingY="30px" paddingX="14px" sx={props.sxContent}>
        {props.tabItems.map((tabItem: any, index) => (
          <TabPanel key={index.toString()} value={props.selectedTab} index={index}>
            <TabContent>{tabItem.content}</TabContent>
          </TabPanel>
        ))}
      </Box>
    </Box>
  );
};

export default Tabs;
