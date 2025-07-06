import React from 'react';
import { Container, Typography, Paper, Box, Switch, FormControlLabel } from '@mui/material';

const Settings = () => {
  return (
    <Container maxWidth="sm" sx={{ mt: 6, mb: 4 }}>
      <Typography variant="h4" gutterBottom>Settings</Typography>
      <Paper sx={{ p: 3 }}>
        <Box mb={2}>
          <Typography variant="h6">User Preferences</Typography>
        </Box>
        <FormControlLabel control={<Switch defaultChecked />} label="Enable notifications" />
        <FormControlLabel control={<Switch />} label="Dark mode" />
        <FormControlLabel control={<Switch />} label="Auto-update dashboard" />
      </Paper>
    </Container>
  );
};

export default Settings; 