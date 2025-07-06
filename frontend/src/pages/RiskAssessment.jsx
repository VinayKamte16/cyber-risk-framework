import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Chip } from '@mui/material';
import { useMockData } from '../contexts/MockDataContext';

const RiskAssessment = () => {
  const { mockData } = useMockData();
  const categories = mockData?.riskAssessment || [];

  return (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="60vh">
      <Typography variant="h4" gutterBottom>Category Risk Scores</Typography>
      <Grid container spacing={3} justifyContent="center" sx={{ maxWidth: 900 }}>
        {categories.map((cat, idx) => (
          <Grid item xs={12} md={4} key={idx}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  {cat.name}
                </Typography>
                <Typography variant="h3" color={cat.level === 'High' ? 'error' : cat.level === 'Medium' ? 'warning.main' : 'success.main'}>
                  {cat.score}
                </Typography>
                <Chip label={cat.level} color={cat.level === 'High' ? 'error' : cat.level === 'Medium' ? 'warning' : 'success'} sx={{ mt: 1, fontWeight: 'bold' }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default RiskAssessment; 