import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import { ListItemIcon, ListItemText, Menu, MenuItem } from '@mui/material';
import { IconButton } from 'lightning-ui/src/design-system/components';
import React, { ReactNode } from 'react';

export type MoreMenuItem = {
  label: string;
  icon: ReactNode;
  onClick: () => void;
  disabled?: boolean;
};

export type MoreMenuProps = {
  id: string;
  items: MoreMenuItem[];
};

const MoreMenu = ({ id, items }: MoreMenuProps) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event: any) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const menuId = open ? id : undefined;

  return (
    <div>
      <IconButton id={menuId + '-button'} aria-controls={menuId} aria-haspopup="true" onClick={handleClick}>
        <MoreHorizIcon sx={{ fontSize: 16 }} />
      </IconButton>
      <Menu
        id={menuId}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}>
        {items.map(item => (
          <MenuItem
            onClick={() => {
              item.onClick();
              handleClose();
            }}
            disabled={item.disabled}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </MenuItem>
        ))}
      </Menu>
    </div>
  );
};

export default MoreMenu;
