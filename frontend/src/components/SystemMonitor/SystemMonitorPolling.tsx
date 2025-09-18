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

const SystemMonitorPolling: React.FC = () => {
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
  const [lastUpdate, setLastUpdate] = useState<number>(0);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const fetchMonitorData = async () => {
    if (!mountedRef.current) return;

    try {
      const response = await fetch('/api/system/monitor');
      const data: MonitorResponse = await response.json();

      if (!mountedRef.current) return;

      if (data.success && data.data) {
        setMonitorData(data.data);
        setError(null);
        setLoading(false);
        setConnectionStatus('connected');
        setLastUpdate(Date.now());
      } else {
        console.error('SystemMonitorPolling: Server error:', data.error);
        setError(data.error || '获取监控数据失败');
        setConnectionStatus('error');
      }
    } catch (err) {
      if (!mountedRef.current) return;
      console.error('SystemMonitorPolling: Fetch error:', err);
      setError('网络请求失败');
      setConnectionStatus('error');
    }
  };

  useEffect(() => {
    mountedRef.current = true;

    // 立即获取一次数据
    fetchMonitorData();

    // 每2秒轮询一次（与SSE频率相同）
    intervalRef.current = setInterval(fetchMonitorData, 2000);

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
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

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#52c41a';
      case 'disconnected': return '#d9d9d9';
      case 'error': return '#f5222d';
      default: return '#d9d9d9';
    }
  };

  const getConnectionStatusText = () => {
    const timeSinceUpdate = Date.now() - lastUpdate;
    if (connectionStatus === 'connected' && timeSinceUpdate < 5000) {
      return '实时';
    }
    switch (connectionStatus) {
      case 'connected': return '已连接';
      case 'disconnected': return '已断开';
      case 'error': return '错误';
      default: return '未知';
    }
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

  if (error && !monitorData) {
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
        <Tooltip title={`连接状态: ${getConnectionStatusText()}`}>
          <div style={{
            display: 'inline-block',
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: getConnectionStatusColor(),
            marginLeft: '8px'
          }} />
        </Tooltip>
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

export default SystemMonitorPolling;