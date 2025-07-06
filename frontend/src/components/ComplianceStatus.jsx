import React from 'react';
import {
  Paper,
  Typography,
  Grid,
  Box,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  useTheme,
} from '@mui/material';
import {
  ExpandMore,
  CheckCircle,
  Error,
  Warning,
} from '@mui/icons-material';

const getStatusIcon = (status) => {
  switch (status.toLowerCase()) {
    case 'compliant':
      return <CheckCircle color="success" />;
    case 'non-compliant':
      return <Error color="error" />;
    case 'partial':
      return <Warning color="warning" />;
    default:
      return <CheckCircle color="disabled" />;
  }
};

const getComplianceColor = (percentage) => {
  if (percentage >= 90) return 'success';
  if (percentage >= 70) return 'warning';
  return 'error';
};

function ComplianceStatus({ compliance = { overallScore: 0, frameworks: [] } }) {
  const theme = useTheme();
  const { overallScore = 0, frameworks = [] } = compliance;

  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Compliance Status
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="subtitle1" sx={{ mr: 1 }}>
            Overall Compliance:
          </Typography>
          <Typography variant="h6" color="primary">
            {overallScore}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={overallScore}
          color={getComplianceColor(overallScore)}
          sx={{ height: 10, borderRadius: 5 }}
        />
      </Box>

      {frameworks.map((framework, index) => (
        <Accordion key={index} defaultExpanded={index === 0}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
              <Typography sx={{ flexGrow: 1 }}>{framework.name}</Typography>
              <Chip
                label={`${framework.score}%`}
                color={getComplianceColor(framework.score)}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <List dense>
              {framework.requirements.map((req, reqIndex) => (
                <ListItem key={reqIndex}>
                  <ListItemIcon>
                    {getStatusIcon(req.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={req.title}
                    secondary={
                      req.status === 'non-compliant' ? req.actionItems : null
                    }
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>
      ))}
    </Paper>
  );
}

export default ComplianceStatus; 