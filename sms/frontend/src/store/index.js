import { configureStore } from '@reduxjs/toolkit';

import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';
import studentReducer from './slices/studentSlice';
import staffReducer from './slices/staffSlice';
import libraryReducer from './slices/librarySlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    student: studentReducer,
    staff: staffReducer,
    library: libraryReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store; 