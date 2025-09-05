import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import styles from './AppRouter.module.css';

// 懒加载页面组件
const HomePage = React.lazy(() => import('@/pages/Home/HomePage'));
const ConfigPage = React.lazy(() => import('@/pages/Config/ConfigPage'));
const AboutPage = React.lazy(() => import('@/pages/About/AboutPage'));
const NotFoundPage = React.lazy(() => import('@/pages/NotFound/NotFoundPage'));

/**
 * 路由加载组件
 */
const RouteLoading: React.FC = () => (
  <div className={styles.loadingContainer}>
    <Spin size='large' tip='正在加载页面...' />
  </div>
);

/**
 * 受保护的路由组件
 */
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredAuth?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredAuth = false }) => {
  // TODO: 实现用户认证逻辑
  const isAuthenticated = true; // 暂时设为 true

  if (requiredAuth && !isAuthenticated) {
    return <Navigate to='/login' replace />;
  }

  return <>{children}</>;
};

/**
 * 应用主路由组件
 * 负责管理所有页面路由和导航逻辑
 */
const AppRouter: React.FC = () => {
  return (
    <div className={styles.routerContainer}>
      <Suspense fallback={<RouteLoading />}>
        <Routes>
          {/* 默认路由重定向 */}
          <Route path='/' element={<Navigate to='/home' replace />} />

          {/* 首页 */}
          <Route
            path='/home'
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />

          {/* 配置管理页面 */}
          <Route
            path='/config'
            element={
              <ProtectedRoute>
                <ConfigPage />
              </ProtectedRoute>
            }
          />

          {/* 配置详情页面 */}
          <Route
            path='/config/:id'
            element={
              <ProtectedRoute>
                <ConfigPage />
              </ProtectedRoute>
            }
          />

          {/* 关于页面 */}
          <Route
            path='/about'
            element={
              <ProtectedRoute>
                <AboutPage />
              </ProtectedRoute>
            }
          />

          {/* 404 页面 */}
          <Route path='/404' element={<NotFoundPage />} />

          {/* 捕获所有未匹配的路由 */}
          <Route path='*' element={<Navigate to='/404' replace />} />
        </Routes>
      </Suspense>
    </div>
  );
};

export default AppRouter;
