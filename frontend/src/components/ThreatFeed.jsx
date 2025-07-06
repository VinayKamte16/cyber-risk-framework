import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';

const getSeverityIcon = (severity) => {
  switch (severity.toLowerCase()) {
    case 'high':
      return <ErrorIcon color="error" />;
    case 'medium':
      return <WarningIcon color="warning" />;
    case 'low':
      return <InfoIcon color="info" />;
    default:
      return <InfoIcon color="info" />;
  }
};

const getSeverityColor = (severity) => {
  switch (severity.toLowerCase()) {
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    case 'low':
      return 'info';
    default:
      return 'default';
  }
};

function ThreatFeed({ threats, onRefresh }) {
  const theme = useTheme();

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <WarningIcon sx={{ mr: 1, color: 'error.main' }} />
            <Typography variant="h6" component="h2">
              Active Threats
            </Typography>
          </Box>
          <Tooltip title="Refresh threats">
            <IconButton onClick={onRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <List sx={{ p: 0 }}>
          {(threats || []).map((threat, index) => (
            <ListItem
              key={index}
              sx={{
                borderBottom: index !== threats.length - 1 ? 1 : 0,
                borderColor: 'divider',
                py: 1.5,
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {getSeverityIcon(threat.severity)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1" component="span">
                      {threat.title}
                    </Typography>
                    <Chip
                      label={threat.severity}
                      size="small"
                      color={getSeverityColor(threat.severity)}
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {threat.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatDistanceToNow(new Date(threat.timestamp), {
                        addSuffix: true,
                      })}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}

export default ThreatFeed; 