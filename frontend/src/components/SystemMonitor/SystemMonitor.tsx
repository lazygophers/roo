import React, { useState, useEffect, useRef } from 'react';
import { Progress, Space, Typography, Tooltip, Alert } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import {
  ClockCircleOutlined,
  ThunderboltOutlined,
  DatabaseOutlined,
  WifiOutlined,
  InfoCircleOutlined
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

const SystemMonitor: React.FC = () => {
  const [monitorData, setMonitorData] = useState<SystemMonitorData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting');

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const mountedRef = useRef(true);

  const connectToSSE = () => {
    if (!mountedRef.current) {
      console.log('Component unmounted, skipping SSE connection');
      return;
    }

    try {
      setConnectionStatus('connecting');
      console.log('Attempting to connect to SSE...');

      // 创建EventSource连接
      const eventSource = new EventSource('/api/system/monitor/stream');
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        if (!mountedRef.current) return;
        console.log('✅ SSE connection opened successfully');
        setConnectionStatus('connected');
        setError(null);
        reconnectAttempts.current = 0; // 重置重连计数
      };

      eventSource.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          console.log('📥 Received SSE data:', event.data.substring(0, 100) + '...');
          const data: MonitorResponse = JSON.parse(event.data);

          if (data.success && data.data) {
            setMonitorData(data.data);
            setError(null);
            setLoading(false);
            console.log('✅ Monitor data updated successfully');
          } else {
            console.error('❌ Server returned error:', data.error);
            setError(data.error || '获取监控数据失败');
          }
        } catch (parseError) {
          console.error('❌ Failed to parse SSE data:', parseError, 'Raw data:', event.data);
          setError('数据解析失败');
        }
      };

      eventSource.onerror = (event) => {
        if (!mountedRef.current) return;
        console.error('❌ SSE connection error:', event);
        console.log('EventSource readyState:', eventSource.readyState);
        setConnectionStatus('error');

        // 自动重连逻辑
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000); // 指数退避，最大10秒
          console.log(`🔄 Will attempt to reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            if (!mountedRef.current) return;
            reconnectAttempts.current++;
            console.log(`🔄 Attempting to reconnect (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`);
            connectToSSE();
          }, delay);
        } else {
          console.error('❌ Max reconnection attempts reached');
          setError('连接失败，已达到最大重试次数');
          setConnectionStatus('disconnected');
        }
      };

    } catch (err) {
      console.error('❌ Failed to create SSE connection:', err);
      setError('无法建立实时连接');
      setConnectionStatus('error');
    }
  };

  const disconnectSSE = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    setConnectionStatus('disconnected');
  };

  useEffect(() => {
    let isMounted = true;

    // 防止快速重连，添加小延迟
    const connectTimer = setTimeout(() => {
      if (isMounted) {
        connectToSSE();
      }
    }, 200);

    return () => {
      isMounted = false;
      mountedRef.current = false;
      clearTimeout(connectTimer);
      disconnectSSE();
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
      case 'connecting': return '#1890ff';
      case 'disconnected': return '#d9d9d9';
      case 'error': return '#f5222d';
      default: return '#d9d9d9';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return '已连接';
      case 'connecting': return '连接中';
      case 'disconnected': return '已断开';
      case 'error': return '连接错误';
      default: return '未知';
    }
  };

  if (loading) {
    return (
      <ProCard size="small" style={{ margin: '8px 0' }}>
        <div style={{ textAlign: 'center', padding: '12px 0' }}>
          <Text type="secondary">正在建立实时连接...</Text>
          <div style={{ marginTop: '8px' }}>
            <div style={{
              display: 'inline-block',
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: getConnectionStatusColor(),
              marginRight: '8px'
            }} />
            <Text style={{ fontSize: '12px' }} type="secondary">
              {getConnectionStatusText()}
            </Text>
          </div>
        </div>
      </ProCard>
    );
  }

  if (error) {
    return (
      <ProCard size="small" style={{ margin: '8px 0' }}>
        <Alert
          message="实时监控连接失败"
          description={
            <div>
              <div>{error}</div>
              <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{
                    display: 'inline-block',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: getConnectionStatusColor(),
                    marginRight: '6px'
                  }} />
                  <Text style={{ fontSize: '11px' }} type="secondary">
                    {getConnectionStatusText()}
                  </Text>
                </div>
                {connectionStatus === 'error' && (
                  <Text
                    style={{ fontSize: '11px', cursor: 'pointer', color: '#1890ff' }}
                    onClick={connectToSSE}
                  >
                    重试连接
                  </Text>
                )}
              </div>
            </div>
          }
          type="warning"
          showIcon
        />
      </ProCard>
    );
  }

  if (!monitorData) {
    return null;
  }

  return (
    <div style={{ padding: '8px 0', borderTop: '1px solid #f0f0f0' }}>
      <div style={{ marginBottom: '8px', paddingLeft: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Text strong style={{ fontSize: '12px' }}>
          <InfoCircleOutlined style={{ marginRight: '4px' }} />
          系统监控
        </Text>
        <Tooltip title={`实时连接状态: ${getConnectionStatusText()}`}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{
              display: 'inline-block',
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: getConnectionStatusColor(),
              marginRight: '4px',
              ...(connectionStatus === 'connecting' ? {
                animation: 'pulse 1.5s infinite'
              } : {})
            }} />
            <Text style={{ fontSize: '10px' }} type="secondary">
              实时
            </Text>
          </div>
        </Tooltip>
      </div>
      
      <Space direction="vertical" size="small" style={{ width: '100%', padding: '0 12px' }}>
        {/* 运行时间 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <ClockCircleOutlined style={{ fontSize: '12px', marginRight: '6px', color: '#1890ff' }} />
            <Text style={{ fontSize: '12px' }}>运行时间</Text>
          </div>
          <Tooltip title={`总共运行 ${Math.floor(monitorData.uptime.total_seconds / 3600)} 小时`}>
            <Text style={{ fontSize: '12px', fontWeight: 500 }}>
              {monitorData.uptime.formatted}
            </Text>
          </Tooltip>
        </div>

        {/* CPU 使用率 */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <ThunderboltOutlined style={{ fontSize: '12px', marginRight: '6px', color: getCPUColor(monitorData.cpu.percent) }} />
              <Text style={{ fontSize: '12px' }}>CPU</Text>
            </div>
            <Text style={{ fontSize: '12px', fontWeight: 500 }}>
              {monitorData.cpu.usage}
            </Text>
          </div>
          <Progress
            percent={monitorData.cpu.percent}
            size="small"
            strokeColor={getCPUColor(monitorData.cpu.percent)}
            showInfo={false}
            style={{ margin: 0 }}
          />
        </div>

        {/* 内存使用 */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <DatabaseOutlined style={{ fontSize: '12px', marginRight: '6px', color: getMemoryColor(monitorData.memory.percent) }} />
              <Text style={{ fontSize: '12px' }}>内存</Text>
            </div>
            <Tooltip title={`内存使用率: ${monitorData.memory.percent.toFixed(1)}%`}>
              <Text style={{ fontSize: '12px', fontWeight: 500 }}>
                {monitorData.memory.used_mb.toFixed(1)}MB
              </Text>
            </Tooltip>
          </div>
          <Progress
            percent={monitorData.memory.percent}
            size="small"
            strokeColor={getMemoryColor(monitorData.memory.percent)}
            showInfo={false}
            style={{ margin: 0 }}
          />
        </div>

        {/* 响应时间 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <WifiOutlined style={{ fontSize: '12px', marginRight: '6px', color: getResponseTimeColor(monitorData.response_time.ms) }} />
            <Text style={{ fontSize: '12px' }}>响应</Text>
          </div>
          <Text style={{ 
            fontSize: '12px', 
            fontWeight: 500,
            color: getResponseTimeColor(monitorData.response_time.ms)
          }}>
            {monitorData.response_time.ms.toFixed(1)}ms
          </Text>
        </div>

        {/* 进程信息 */}
        <div style={{ marginTop: '6px', paddingTop: '6px', borderTop: '1px solid #f0f0f0' }}>
          <Tooltip title={`PID: ${monitorData.process.pid} | 线程: ${monitorData.process.num_threads} | 状态: ${monitorData.process.status}`}>
            <Text type="secondary" style={{ fontSize: '11px' }}>
              {monitorData.process.name} • {monitorData.process.num_threads} 线程
            </Text>
          </Tooltip>
        </div>
      </Space>
    </div>
  );
};

export default SystemMonitor;