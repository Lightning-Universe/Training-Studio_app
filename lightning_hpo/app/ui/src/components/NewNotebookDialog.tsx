import { Dialog, DialogActions, DialogContent, ToggleButton } from '@mui/material';
import { Box, Button, DialogTitle, Stack, TextField } from 'lightning-ui/src/design-system/components';
import FormControl from 'lightning-ui/src/design-system/components/form-control';
import React, { useReducer } from 'react';
import { NotebookConfig } from '../generated';
import { appClient } from '../hooks/useClientDataState';
import LightningToggleButtonGroup from './LightningToggleButtonGroup';

export type NewNotebookDialogProps = {
  open: boolean;
  setOpen: (value: boolean) => void;
};

const NewNotebookDialog = ({ open, setOpen }: NewNotebookDialogProps) => {
  const [config, setConfig] = useReducer(
    (config: NotebookConfig, newConfig: Partial<NotebookConfig>) => {
      return { ...config, ...newConfig };
    },
    { notebook_name: '', cloud_compute: 'cpu', requirements: [] },
  );

  const cancel = () => {
    setOpen(false);
  };

  const confirm = () => {
    appClient.appClientCommand.runNotebookCommandRunNotebookPost(config);
    setOpen(false);
  };

  return (
    <Dialog open={open} onClose={cancel}>
      <DialogTitle text="New notebook" onCloseClick={cancel} />
      <DialogContent sx={{ padding: '16px 24px', minWidth: { xs: '0px', sm: '400px' } }}>
        <Stack direction="column" spacing={2}>
          <TextField
            label="Name"
            value={config.notebook_name}
            onChange={value => setConfig({ notebook_name: value || '' })}
            fullWidth
          />
          <FormControl label="Hardware" fullWidth>
            <LightningToggleButtonGroup
              color="primary"
              value={config.cloud_compute}
              exclusive
              onChange={(event, value) => (value != null ? setConfig({ cloud_compute: value }) : null)}
              fullWidth>
              <ToggleButton value="cpu">CPU</ToggleButton>
              <ToggleButton value="gpu">Cheap GPU</ToggleButton>
              <ToggleButton value="gpu-fast">Fast GPU</ToggleButton>
            </LightningToggleButtonGroup>
          </FormControl>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ padding: '16px 24px' }}>
        <Box component={'div'} display={'flex'} justifyContent={'end'} width={'100%'}>
          <Button size="small" variant="contained" text="Cancel" color={'grey'} onClick={cancel} />
          <Box component={'div'} px={0.5} />
          <Button size="small" variant="contained" text="Create" onClick={confirm} />
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default NewNotebookDialog;
