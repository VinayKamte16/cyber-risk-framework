import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface RiskScore {
  timestamp: string;
  scores: {
    final: number;
    anomaly: number;
    risk_probability: number;
  };
  explanations: {
    lime: Array<{
      feature: string;
      importance: number;
    }>;
  };
}

const RiskDashboard: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskData, setRiskData] = useState<RiskScore[]>([]);
  const [historicalData, setHistoricalData] = useState<any[]>([]);

  const COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.error.main,
    theme.palette.warning.main,
  ];

  useEffect(() => {
    fetchRiskData();
    const interval = setInterval(fetchRiskData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchRiskData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/risk/score`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch risk data');
      }

      const data = await response.json();
      setRiskData([...riskData, data]);
      updateHistoricalData(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(false);
    }
  };

  const updateHistoricalData = (newData: RiskScore) => {
    const newHistorical = [...historicalData];
    if (newHistorical.length > 20) {
      newHistorical.shift();
    }
    const dateObj = new Date(newData.timestamp);
    const formattedTime = dateObj.getHours().toString().padStart(2, '0') + ':' + dateObj.getMinutes().toString().padStart(2, '0');
    newHistorical.push({
      timestamp: formattedTime,
      riskScore: newData.scores.final * 100,
      anomalyScore: newData.scores.anomaly * 100,
    });
    setHistoricalData(newHistorical);
  };

  const getRiskLevel = (score: number): string => {
    if (score < 0.3) return 'Low';
    if (score < 0.7) return 'Medium';
    return 'High';
  };

  const getRiskColor = (score: number): string => {
    if (score < 0.3) return theme.palette.success.main;
    if (score < 0.7) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const currentRisk = riskData[riskData.length - 1];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Risk Score Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Risk Score
              </Typography>
              <Typography variant="h3" component="div" sx={{ color: getRiskColor(currentRisk.scores.final) }}>
                {Math.round(currentRisk.scores.final * 100)}%
              </Typography>
              <Typography variant="subtitle1" sx={{ mt: 1 }}>
                Risk Level: {getRiskLevel(currentRisk.scores.final)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Anomaly Score Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Anomaly Detection
              </Typography>
              <Typography variant="h3" component="div">
                {Math.round(currentRisk.scores.anomaly * 100)}%
              </Typography>
              <Typography variant="subtitle1" sx={{ mt: 1 }}>
                Deviation from normal behavior
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Probability Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Probability
              </Typography>
              <Typography variant="h3" component="div">
                {Math.round(currentRisk.scores.risk_probability * 100)}%
              </Typography>
              <Typography variant="subtitle1" sx={{ mt: 1 }}>
                ML-based prediction
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Historical Trend Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Risk Score Trend
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tick={{ angle: 45, textAnchor: 'start' }} />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="riskScore"
                  stroke={theme.palette.primary.main}
                  name="Risk Score"
                />
                <Line
                  type="monotone"
                  dataKey="anomalyScore"
                  stroke={theme.palette.secondary.main}
                  name="Anomaly Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Feature Importance */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Feature Importance
            </Typography>
            <Box sx={{ height: 300 }}>
              {currentRisk.explanations.lime && (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={currentRisk.explanations.lime.slice(0, 5)}
                      dataKey="importance"
                      nameKey="feature"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {currentRisk.explanations.lime.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default RiskDashboard; 