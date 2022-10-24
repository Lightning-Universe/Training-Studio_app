import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { Card, CardContent, Tooltip, Typography } from '@mui/material';
import { Box, IconButton, Stack } from 'lightning-ui/src/design-system/components';
import React, { useState } from 'react';
import cloud from '../assets/cloud.svg';

export type UserGuideProps = {
  title: string;
  subtitle: string;
  children: React.ReactNode;
};

export const UserGuideComment = ({ children }: { children: string }) => {
  return (
    <Typography
      sx={{
        fontSize: '14px',
        fontFamily: 'Roboto Mono',
        fontWeight: '400',
        fontStyle: 'normal',
        lineHeight: '18px',
        color: 'primary.70',
        marginTop: '18px',
      }}>
      # {children}
    </Typography>
  );
};

export type UserGuideBodyProps = {
  children: React.ReactNode;
};

export const UserGuideBody = ({ children }: UserGuideBodyProps) => {
  const [tooltip, setTooltip] = useState('Copy command');

  const copyText = (text: string) => {
    window.navigator?.clipboard?.writeText(text);
    setTooltip('Copied!');
  };

  return (
    <Typography
      sx={{
        fontSize: '14px',
        fontFamily: 'Roboto Mono',
        fontWeight: '400',
        fontStyle: 'normal',
        lineHeight: '18px',
        color: 'grey.100',
      }}>
      {children}
      <Tooltip title={tooltip} onOpen={() => setTooltip('Copy command')}>
        <IconButton
          sx={{ margin: '0px 8px', padding: '0px' }}
          aria-label="copy"
          onClick={() => copyText(children as string)}>
          <ContentCopyIcon sx={{ fontSize: 16 }} />
        </IconButton>
      </Tooltip>
    </Typography>
  );
};

const UserGuide = ({ title, subtitle, children }: UserGuideProps) => {
  return (
    <Stack
      alignItems="center"
      direction="column"
      spacing={3}
      width="100%"
      sx={{ marginTop: { xs: '0px', sm: '125px' } }}>
      <img src={cloud} alt="Cloud" width="100px" />
      <Stack alignItems="center" direction="column" spacing={0.5}>
        <Typography
          sx={{
            fontSize: '16px',
            fontFamily: 'Ucity',
            fontWeight: '600',
            fontStyle: 'normal',
            lineHeight: '20px',
            color: 'rgba(5, 5, 5, 1)',
          }}>
          {title}
        </Typography>
        <Typography sx={{ color: '#65676B' }} variant="body2">
          {subtitle}
        </Typography>
      </Stack>
      <Card elevation={2} sx={{ position: 'relative', borderRadius: '10px', backgroundColor: 'grey.10' }}>
        <Stack direction="row" sx={{ position: 'absolute', left: '10px', top: '10px' }} spacing="8px">
          <Box sx={{ borderRadius: '50%', width: '12px', height: '12px', backgroundColor: 'grey.20' }} />
          <Box sx={{ borderRadius: '50%', width: '12px', height: '12px', backgroundColor: 'grey.20' }} />
          <Box sx={{ borderRadius: '50%', width: '12px', height: '12px', backgroundColor: 'grey.20' }} />
        </Stack>
        <CardContent sx={{ width: { xs: 'auto', md: '614px' } }}>{children}</CardContent>
      </Card>
    </Stack>
  );
};

export default UserGuide;
