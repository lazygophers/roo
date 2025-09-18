import React, { useState, useEffect, useRef } from 'react';
import { Typography, Progress, Tooltip, theme } from 'antd';
import { 
  MonitorOutlined,
  ThunderboltOutlined, 
  DatabaseOutlined,
  WifiOutlined
} from '@ant-design/icons';

const { Text } = Typography;

interface SystemMonitorData {
  uptime: {
    formatted: string;
    total_seconds: number;
  };
  cpu: {
    percent: number;
    usage: string;
  };
  memory: {
    used_mb: number;
    percent: number;
    formatted: string;
  };
  response_time: {
    ms: number;
  };
  process: {
    pid: number;
    name: string;
    status: string;
    num_threads: number;
  };
  server_time: string;
}

interface MonitorResponse {
  success: boolean;
  data: SystemMonitorData;
  error?: string;
}

const SystemMonitorMenuItem: React.FC = () => {
  const {
    token: { 
      colorBorderSecondary, 
      colorText,
      colorTextSecondary,
      colorTextTertiary,
      colorBgLayout
    },
  } = theme.useToken();
  
  const [monitorData, setMonitorData] = useState<SystemMonitorData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected');

  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    let isMounted = true;
    console.log('SystemMonitorMenuItem: Starting SSE connection...');

    // 防止快速重连，添加小延迟
    const connectTimer = setTimeout(() => {
      if (!isMounted) return;

      // 创建SSE连接
      const eventSource = new EventSource('/api/system/monitor/stream');
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        if (!isMounted) return;
        console.log('SystemMonitorMenuItem: SSE connection opened');
        setConnectionStatus('connected');
        setError(null);
      };

      eventSource.onmessage = (event) => {
        if (!isMounted) return;
        try {
          const data: MonitorResponse = JSON.parse(event.data);

          if (data.success && data.data) {
            setMonitorData(data.data);
            setError(null);
            setLoading(false);
            console.log('SystemMonitorMenuItem: Data updated');
          } else {
            console.error('SystemMonitorMenuItem: Server error:', data.error);
            setError(data.error || '获取监控数据失败');
          }
        } catch (parseError) {
          console.error('SystemMonitorMenuItem: Parse error:', parseError);
          setError('数据解析失败');
        }
      };

      eventSource.onerror = (event) => {
        if (!isMounted) return;
        console.error('SystemMonitorMenuItem: SSE error:', event);
        console.log('SystemMonitorMenuItem: EventSource readyState:', eventSource.readyState);

        // 检查错误类型
        if (eventSource.readyState === EventSource.CLOSED) {
          console.log('SystemMonitorMenuItem: Connection was closed');
          setConnectionStatus('disconnected');
        } else {
          setConnectionStatus('error');
        }
        setError('实时连接异常');
      };
    }, 100); // 100ms延迟防止快速重连

    return () => {
      isMounted = false;
      clearTimeout(connectTimer);
      console.log('SystemMonitorMenuItem: Cleaning up SSE connection');
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  const getCPUColor = (percent: number): string => {
    if (percent < 50) return '#52c41a'; // 绿色
    if (percent < 80) return '#faad14'; // 橙色
    return '#f5222d'; // 红色
  };

  const getMemoryColor = (percent: number): string => {
    if (percent < 60) return '#52c41a'; // 绿色
    if (percent < 85) return '#faad14'; // 橙色
    return '#f5222d'; // 红色
  };

  const getResponseTimeColor = (ms: number): string => {
    if (ms < 100) return '#52c41a'; // 绿色
    if (ms < 500) return '#faad14'; // 橙色
    return '#f5222d'; // 红色
  };

  if (loading) {
    return (
      <div style={{ 
        padding: '12px 24px',
        minHeight: '48px',
        display: 'flex',
        alignItems: 'center',
        color: colorTextSecondary,
        fontSize: '12px'
      }}>
        <MonitorOutlined style={{ marginRight: '8px' }} />
        加载中...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '12px 24px',
        minHeight: '48px',
        display: 'flex',
        alignItems: 'center',
        color: '#ff4d4f',
        fontSize: '12px'
      }}>
        <MonitorOutlined style={{ marginRight: '8px' }} />
        监控异常
      </div>
    );
  }

  if (!monitorData) {
    return null;
  }

  return (
    <div style={{ 
      padding: '8px 24px',
      borderTop: `1px solid ${colorBorderSecondary}`,
      backgroundColor: colorBgLayout
    }}>
      {/* 标题行 */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: '8px',
        fontSize: '12px',
        fontWeight: 500
      }}>
        <MonitorOutlined style={{ marginRight: '6px', color: '#1890ff' }} />
        <Text style={{ fontSize: '12px', color: colorTextSecondary }}>系统监控</Text>
        <Text style={{ 
          fontSize: '11px', 
          color: colorTextTertiary,
          marginLeft: 'auto'
        }}>
          {monitorData.uptime.formatted}
        </Text>
      </div>

      {/* 监控指标 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {/* CPU 使用率 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ThunderboltOutlined style={{ 
            fontSize: '10px', 
            color: getCPUColor(monitorData.cpu.percent),
            minWidth: '10px'
          }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text style={{ fontSize: '11px', color: colorTextSecondary }}>CPU</Text>
              <Text style={{ fontSize: '11px', color: colorText, fontWeight: 500 }}>
                {monitorData.cpu.usage}
              </Text>
            </div>
            <Progress
              percent={monitorData.cpu.percent}
              size="small"
              strokeColor={getCPUColor(monitorData.cpu.percent)}
              showInfo={false}
              style={{ margin: 0, height: '4px' }}
            />
          </div>
        </div>

        {/* 内存使用 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <DatabaseOutlined style={{ 
            fontSize: '10px', 
            color: getMemoryColor(monitorData.memory.percent),
            minWidth: '10px'
          }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text style={{ fontSize: '11px', color: colorTextSecondary }}>内存</Text>
              <Text style={{ fontSize: '11px', color: colorText, fontWeight: 500 }}>
                {monitorData.memory.used_mb.toFixed(1)}MB
              </Text>
            </div>
            <div style={{ 
              height: '4px', 
              backgroundColor: colorBorderSecondary, 
              borderRadius: '2px', 
              overflow: 'hidden',
              position: 'relative'
            }}>
              <div style={{
                height: '100%',
                width: `${Math.min(monitorData.memory.percent, 100)}%`,
                backgroundColor: getMemoryColor(monitorData.memory.percent),
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>
        </div>

        {/* 响应时间 */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginTop: '2px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <WifiOutlined style={{ 
              fontSize: '10px', 
              color: getResponseTimeColor(monitorData.response_time.ms)
            }} />
            <Text style={{ fontSize: '11px', color: colorTextSecondary }}>响应</Text>
          </div>
          <Text style={{ 
            fontSize: '11px', 
            color: getResponseTimeColor(monitorData.response_time.ms),
            fontWeight: 500
          }}>
            {monitorData.response_time.ms.toFixed(1)}ms
          </Text>
        </div>

        {/* 进程信息 */}
        <Tooltip title={`PID: ${monitorData.process.pid} | 线程: ${monitorData.process.num_threads} | 状态: ${monitorData.process.status}`}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginTop: '2px'
          }}>
            <Text style={{ fontSize: '10px', color: colorTextTertiary }}>
              PID {monitorData.process.pid}
            </Text>
            <Text style={{ fontSize: '10px', color: colorTextTertiary }}>
              {monitorData.process.num_threads} 线程
            </Text>
          </div>
        </Tooltip>
      </div>
    </div>
  );
};

export default SystemMonitorMenuItem;