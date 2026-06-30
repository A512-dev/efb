import React from 'react'; 
import '../assets/theme.css';
import AppRouter from '../router/AppRouter';
import AuthProvider from '../auth/AuthProvider';

import { BookmarkProvider } from '../Context/BookmarkContext.jsx';
import { NotificationProvider } from '../Context/NotificationContext.jsx';
const App = () => {
  return (
    <AuthProvider>
      <NotificationProvider>
      <BookmarkProvider>
        <AppRouter />
      </BookmarkProvider>
      </NotificationProvider>
     
    </AuthProvider>
  );
};

export default App;
