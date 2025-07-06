import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  useTheme,
} from '@mui/material';
import { Assessment } from '@mui/icons-material';

function getRiskLevel(score) {
  if (score >= 80) return { level: 'Critical', color: 'error.main' };
  if (score >= 60) return { level: 'High', color: 'warning.main' };
  if (score >= 40) return { level: 'Medium', color: 'info.main' };
  if (score >= 20) return { level: 'Low', color: 'success.main' };
  return { level: 'Very Low', color: 'success.light' };
}

function RiskScoreCard({ score }) {
  const theme = useTheme();
  const riskLevel = getRiskLevel(score);
  const progressValue = (score / 100) * 100;

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'visible',
      }}
    >
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <Assessment sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Current Risk Score
          </Typography>
        </Box>

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            height: 200,
          }}
        >
          <CircularProgress
            variant="determinate"
            value={progressValue}
            size={150}
            thickness={4}
            sx={{
              color: riskLevel.color,
              position: 'absolute',
            }}
          />
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Typography
              variant="h2"
              component="div"
              sx={{ fontWeight: 'bold' }}
            >
              {score}
            </Typography>
            <Typography
              variant="h6"
              sx={{ color: riskLevel.color, fontWeight: 'medium' }}
            >
              {riskLevel.level}
            </Typography>
          </Box>
        </Box>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 2, textAlign: 'center' }}
        >
          Last updated: {new Date().toLocaleTimeString()}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default RiskScoreCard; 