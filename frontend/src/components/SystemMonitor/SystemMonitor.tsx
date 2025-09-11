import React, { useState, useEffect } from 'react';
import { Card, Progress, Space, Typography, Tooltip, Alert } from 'antd';
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

  const fetchMonitorData = async () => {
    try {
      const response = await fetch('/api/system/monitor');
      const data: MonitorResponse = await response.json();
      
      if (data.success) {
        setMonitorData(data.data);
        setError(null);
      } else {
        setError(data.error || '获取监控数据失败');
      }
    } catch (err) {
      setError('网络请求失败');
      console.error('Monitor data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonitorData();
    
    // 每5秒更新一次数据
    const interval = setInterval(fetchMonitorData, 5000);
    
    return () => clearInterval(interval);
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
      <Card size="small" style={{ margin: '8px 0' }}>
        <div style={{ textAlign: 'center', padding: '12px 0' }}>
          <Text type="secondary">加载监控数据...</Text>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card size="small" style={{ margin: '8px 0' }}>
        <Alert
          message="监控数据获取失败"
          description={error}
          type="warning"
          showIcon
        />
      </Card>
    );
  }

  if (!monitorData) {
    return null;
  }

  return (
    <div style={{ padding: '8px 0', borderTop: '1px solid #f0f0f0' }}>
      <div style={{ marginBottom: '8px', paddingLeft: '12px' }}>
        <Text strong style={{ fontSize: '12px' }}>
          <InfoCircleOutlined style={{ marginRight: '4px' }} />
          系统监控
        </Text>
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
            <Tooltip title={`使用 ${monitorData.memory.used_mb.toFixed(1)} MB`}>
              <Text style={{ fontSize: '12px', fontWeight: 500 }}>
                {monitorData.memory.percent.toFixed(1)}%
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