import React from 'react';
import {
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Box,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Computer,
  Storage,
  Cloud,
  Info,
} from '@mui/icons-material';

const getAssetIcon = (type) => {
  switch (type.toLowerCase()) {
    case 'server':
      return <Storage />;
    case 'cloud':
      return <Cloud />;
    default:
      return <Computer />;
  }
};

const getHealthColor = (health) => {
  if (health >= 80) return 'success';
  if (health >= 60) return 'warning';
  return 'error';
};

export const AssetOverview = ({ assets }) => {
  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Asset Overview
        </Typography>
        <Tooltip title="Asset health is calculated based on vulnerabilities, patches, and security configurations">
          <IconButton size="small">
            <Info />
          </IconButton>
        </Tooltip>
      </Box>
      <Grid container spacing={2}>
        {(assets || []).map((asset, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  {getAssetIcon(asset.type)}
                  <Typography variant="subtitle1" sx={{ ml: 1 }}>
                    {asset.name}
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {asset.type} • {asset.ip_address}
                </Typography>
                <Box display="flex" alignItems="center" mt={2}>
                  <Box flex={1} mr={2}>
                    <LinearProgress
                      variant="determinate"
                      value={asset.health}
                      color={getHealthColor(asset.health)}
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {asset.health}%
                  </Typography>
                </Box>
                <Typography variant="caption" color="textSecondary" display="block" mt={1}>
                  Last updated: {new Date(asset.last_updated).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
}; 