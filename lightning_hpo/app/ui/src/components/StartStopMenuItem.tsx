import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import StopCircleIcon from '@mui/icons-material/StopCircle';

const StartStopMenuItem = (status: string, onStart: () => void, onStop: () => void) => {
  if (['stopped', 'not_started'].indexOf(status) >= 0) {
    return {
      label: 'Start',
      icon: <PlayCircleIcon sx={{ fontSize: 20 }} />,
      onClick: onStart,
    };
  }
  return {
    label: 'Stop',
    icon: <StopCircleIcon sx={{ fontSize: 20 }} />,
    onClick: onStop,
  };
};

export default StartStopMenuItem;
