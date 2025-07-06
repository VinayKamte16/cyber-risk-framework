import React from 'react';
import { Box, Typography, Paper, Accordion, AccordionSummary, AccordionDetails, Chip, LinearProgress, Button, Container } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useMockData } from '../contexts/MockDataContext';

const Compliance = () => {
  const { mockData } = useMockData();
  const compliance = mockData?.compliance || { overallScore: 0, frameworks: [] };

  const getColor = (status) => {
    if (status === 'compliant') return 'success';
    if (status === 'partial') return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="md" sx={{ mt: 6, mb: 4 }}>
      <Typography variant="h4" gutterBottom>Compliance</Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6">Overall Compliance</Typography>
        <Typography variant="h2" color={compliance.overallScore > 80 ? 'success.main' : compliance.overallScore > 60 ? 'warning.main' : 'error'}>
          {compliance.overallScore}%
        </Typography>
        <LinearProgress variant="determinate" value={compliance.overallScore} color={compliance.overallScore > 80 ? 'success' : compliance.overallScore > 60 ? 'warning' : 'error'} sx={{ height: 10, borderRadius: 5, mt: 1 }} />
      </Paper>
      {compliance.frameworks.map((fw, idx) => (
        <Accordion key={idx} defaultExpanded={idx === 0}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography sx={{ flexGrow: 1 }}>{fw.name}</Typography>
            <Chip label={`${fw.score}%`} color={fw.score > 80 ? 'success' : fw.score > 60 ? 'warning' : 'error'} size="small" />
          </AccordionSummary>
          <AccordionDetails>
            {fw.requirements.map((req, i) => (
              <Box key={i} display="flex" alignItems="center" mb={1}>
                <Chip label={req.status} color={getColor(req.status)} size="small" sx={{ mr: 2 }} />
                <Typography>{req.title}</Typography>
              </Box>
            ))}
          </AccordionDetails>
        </Accordion>
      ))}
    </Container>
  );
};

export default Compliance; 