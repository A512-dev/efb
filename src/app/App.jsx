import React from 'react'; 
import '../assets/theme.css';
import AppRouter from '../router/AppRouter';
import AuthProvider from '../auth/AuthProvider';

import { BookmarkProvider } from '../auth/BookmarkContext.jsx';

const App = () => {
  return (
    <AuthProvider>
      
      <BookmarkProvider>
        <AppRouter />
      </BookmarkProvider>
    </AuthProvider>
  );
};

export default App;
