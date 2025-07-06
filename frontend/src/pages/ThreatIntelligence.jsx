import React from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, Chip, Container } from '@mui/material';
import { useMockData } from '../contexts/MockDataContext';

const ThreatIntelligence = () => {
  const { mockData } = useMockData();
  const threats = mockData?.threatIntelligence || [];

  return (
    <Container maxWidth="md" sx={{ mt: 6, mb: 4 }}>
      <Typography variant="h4" gutterBottom>Threat Intelligence</Typography>
      <Paper sx={{ p: 3 }}>
        <List>
          {threats.map((threat, idx) => (
            <ListItem key={idx} alignItems="flex-start" divider>
              <ListItemText
                primary={
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="h6">{threat.title}</Typography>
                    <Chip label={threat.severity} color={threat.severity === 'High' ? 'error' : threat.severity === 'Medium' ? 'warning' : 'success'} />
                  </Box>
                }
                secondary={
                  <>
                    <Typography variant="body2">{threat.description}</Typography>
                    <Typography variant="caption" color="text.secondary">{threat.timestamp}</Typography>
                  </>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );
};

export default ThreatIntelligence; 