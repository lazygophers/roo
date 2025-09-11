import React from 'react';
import { Alert, Button } from 'antd';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // 过滤掉浏览器扩展相关的错误
    const isExtensionError = 
      error.message?.includes('extension') ||
      error.message?.includes('content_script') ||
      error.stack?.includes('chrome-extension') ||
      error.stack?.includes('moz-extension');

    if (isExtensionError) {
      // 对于扩展错误，直接重置状态，不显示错误界面
      this.setState({ hasError: false, error: null, errorInfo: null });
      return;
    }

    this.setState({
      error,
      errorInfo,
    });

    // 记录非扩展错误
    console.error('Application Error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px' }}>
          <Alert
            message="应用程序发生错误"
            description="页面出现了意外错误，请重试或刷新页面。"
            type="error"
            action={
              <Button size="small" danger onClick={this.handleRetry}>
                重试
              </Button>
            }
            showIcon
          />
          {process.env.NODE_ENV === 'development' && (
            <details style={{ marginTop: '10px' }}>
              <summary>错误详情（仅开发环境显示）</summary>
              <pre style={{ 
                backgroundColor: '#f5f5f5', 
                padding: '10px', 
                overflow: 'auto',
                fontSize: '12px'
              }}>
                {this.state.error && this.state.error.toString()}
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;