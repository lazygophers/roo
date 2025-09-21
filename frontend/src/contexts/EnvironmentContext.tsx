import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient, PermissionsResponse } from '../api';

interface EnvironmentContextType {
  environment: 'local' | 'remote';
  isRemote: boolean;
  isLocal: boolean;
  isEditAllowed: boolean;
  loading: boolean;
  error: string | null;
  refreshPermissions: () => Promise<void>;
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined);

interface EnvironmentProviderProps {
  children: ReactNode;
}

export const EnvironmentProvider: React.FC<EnvironmentProviderProps> = ({ children }) => {
  const [environment, setEnvironment] = useState<'local' | 'remote'>('local');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isRemote = environment === 'remote';
  const isLocal = environment === 'local';
  const isEditAllowed = isLocal; // 只有在本地环境下才允许编辑

  const refreshPermissions = async () => {
    try {
      setLoading(true);
      setError(null);

      const response: PermissionsResponse = await apiClient.getPermissions();

      if (response.success) {
        setEnvironment(response.data.environment);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取权限信息失败');
      console.error('Failed to fetch permissions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshPermissions();
  }, []);

  const value: EnvironmentContextType = {
    environment,
    isRemote,
    isLocal,
    isEditAllowed,
    loading,
    error,
    refreshPermissions,
  };


  return (
    <EnvironmentContext.Provider value={value}>
      {children}
    </EnvironmentContext.Provider>
  );
};

export const useEnvironment = (): EnvironmentContextType => {
  const context = useContext(EnvironmentContext);
  if (context === undefined) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider');
  }
  return context;
};

export default EnvironmentContext;