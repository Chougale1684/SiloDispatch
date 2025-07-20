const config = {
    api: {
      baseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api',
    },
    map: {
      apiKey: process.env.REACT_APP_MAP_API_KEY || '',
      provider: process.env.REACT_APP_MAP_PROVIDER || 'google',
    },
  };
  
  if (!config.map.apiKey) {
    console.warn('Missing map API key - map features will be disabled');
  }
  
  export default config;