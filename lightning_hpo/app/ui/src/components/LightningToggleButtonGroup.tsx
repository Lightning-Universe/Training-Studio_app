import { styled } from '@mui/material/styles';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

const LightningToggleButtonGroup = styled(ToggleButtonGroup)(({ theme }) => ({
  '& .MuiToggleButtonGroup-grouped': {
    'margin': theme.spacing(0.5),
    'border': 0,
    'borderRadius': 2,
    'height': 28,
    'gap': 8,
    'padding': '4px 8px',
    'color': '#5B5E69',
    'backgroundColor': 'rgba(0, 0, 0, 0.1)',
    'textTransform': 'none',
    '&.Mui-disabled': {
      border: 0,
    },
    '&.Mui-selected': {
      color: theme.palette.primary['main'],
      backgroundColor: (theme.palette.primary as unknown as { '10': string })['10'],
    },
    '&:first-of-type': {
      marginLeft: '0px',
      borderBottomLeftRadius: 20,
      borderTopLeftRadius: 20,
    },
    '&:last-of-type': {
      marginRight: '0px',
      borderBottomRightRadius: 20,
      borderTopRightRadius: 20,
    },
  },
}));

export default LightningToggleButtonGroup;
