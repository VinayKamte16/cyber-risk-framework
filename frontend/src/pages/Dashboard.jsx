import React from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Alert,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Assessment,
  Security,
  Warning,
  CheckCircle,
  Refresh,
  Info,
  Logout,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';
import { useAuth } from '../contexts/AuthContext';
import { useMockData } from '../contexts/MockDataContext';
import RiskScoreCard from '../components/RiskScoreCard';
import ThreatFeed from '../components/ThreatFeed';
import { AssetOverview } from '../components/AssetOverview';
import ComplianceStatus from '../components/ComplianceStatus';

function Dashboard() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { logout } = useAuth();
  const { mockData } = useMockData();

  if (!mockData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  const dashboardData = mockData.dashboard;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Cybersecurity Risk Dashboard
        </Typography>
        <Tooltip title="Logout">
          <IconButton onClick={logout} color="primary">
            <Logout />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* Risk Score Card */}
        <Grid item xs={12} md={4}>
          <RiskScoreCard score={dashboardData.currentRiskScore} />
        </Grid>

        {/* Active Threats */}
        <Grid item xs={12} md={8}>
          <ThreatFeed threats={dashboardData.threats} />
        </Grid>

        {/* Risk Score Trend */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, height: '400px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Risk Score Trend
            </Typography>
            <Box sx={{ flexGrow: 1 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dashboardData.riskScores}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" tickFormatter={(tick) => tick.split('T')[0]} />
                  <YAxis domain={[0, 100]} />
                  <ChartTooltip />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke={theme.palette.primary.main}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Assets Overview */}
        <Grid item xs={12} md={6}>
          <AssetOverview assets={dashboardData.assets} />
        </Grid>

        {/* Compliance Status */}
        <Grid item xs={12} md={6}>
          <ComplianceStatus compliance={dashboardData.compliance} />
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard; 