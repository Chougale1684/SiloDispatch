import React, { useState, createContext } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { theme } from './api/theme';
import Dashboard from './pages/Dashboard';
import Batches from './pages/Batches';
import Tracking from './pages/Tracking';
import Settlements from './pages/Settlements';

// Define AuthContext and its type
export const AuthContext = createContext({
  user: null,
  setUser: (_user: any) => {},
});

const queryClient = new QueryClient();

function App() {
  const [user, setUser] = useState(null);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/batches" element={<Batches />} />
              <Route path="/tracking" element={<Tracking />} />
              <Route path="/settlements" element={<Settlements />} />
            </Routes>
          </BrowserRouter>
        </QueryClientProvider>
      </ThemeProvider>
    </AuthContext.Provider>
  );
}

export default App;