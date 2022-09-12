import AddCircleIcon from '@mui/icons-material/AddCircle';
import { ListItemText, Menu, MenuItem } from '@mui/material';
import { Button } from 'lightning-ui/src/design-system/components';
import React from 'react';
import NewNotebookDialog from './NewNotebookDialog';

const NewMenu = () => {
  const [notebookDialogOpen, setNotebookDialogOpen] = React.useState(false);
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event: any) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const menuId = open ? 'new' : undefined;

  return (
    <div>
      <Button
        text="New"
        icon={<AddCircleIcon sx={{ fontSize: 20 }} />}
        color="primary"
        variant="contained"
        size="small"
        aria-controls={menuId}
        aria-haspopup="true"
        onClick={handleClick}
      />
      <Menu
        id={menuId}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}>
        <MenuItem
          onClick={() => {
            setNotebookDialogOpen(true);
            handleClose();
          }}>
          <ListItemText primary="Notebook" />
        </MenuItem>
      </Menu>
      <NewNotebookDialog open={notebookDialogOpen} setOpen={setNotebookDialogOpen} />
    </div>
  );
};

export default NewMenu;
