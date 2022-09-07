import { Box } from '@mui/material';
import { Card, CardContent, CardHeader } from 'lightning-ui/src/design-system/components';
import { ReactNode } from 'react';

export type TableContainerProps = {
  header: string;
  children: ReactNode;
};

const TableContainer = (props: TableContainerProps) => {
  return (
    <Box sx={{ padding: '24px' }}>
      <Card width="100%">
        <CardHeader title={props.header} />
        <CardContent>{props.children}</CardContent>
      </Card>
    </Box>
  );
};

export default TableContainer;
