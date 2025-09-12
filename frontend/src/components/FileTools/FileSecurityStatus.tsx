import React, { useState, useEffect } from 'react';
import {
  Card,
  Statistic,
  Tag,
  Space,
  Button,
  Modal,
  Row,
  Col,
  Typography,
  Badge,
  Tooltip,
  Progress,
  Alert
} from 'antd';
import {
  SecurityScanOutlined,
  LockOutlined,
  UnlockOutlined,
  FolderOpenOutlined,
  InfoCircleOutlined,
  SettingOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiClient, FileSecurityInfo } from '../../api';
import { useTheme } from '../../contexts/ThemeContext';

const { Title, Text, Paragraph } = Typography;

interface FileSecurityStatusProps {
  showTitle?: boolean;
  compact?: boolean;
}

const FileSecurityStatus: React.FC<FileSecurityStatusProps> = ({ 
  showTitle = true, 
  compact = false 
}) => {
  const navigate = useNavigate();
  const { currentTheme } = useTheme();
  const [loading, setLoading] = useState(false);
  const [securityInfo, setSecurityInfo] = useState<FileSecurityInfo | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  // 解析安全配置信息
  const parseSecurityInfo = (content: string): Partial<FileSecurityInfo> => {
    const lines = content.split('\n');
    const info: Partial<FileSecurityInfo> = {
      readable_directories: [],
      writable_directories: [],
      deletable_directories: [],
      forbidden_directories: [],
      max_file_size_mb: 0,
      max_read_lines: 0,
      strict_mode: false
    };
    
    let currentSection = '';
    
    lines.forEach((line: string) => {
      const trimmed = line.trim();
      if (trimmed.includes('可读取目录')) {
        currentSection = 'readable_directories';
      } else if (trimmed.includes('可写入目录')) {
        currentSection = 'writable_directories';
      } else if (trimmed.includes('可删除目录')) {
        currentSection = 'deletable_directories';
      } else if (trimmed.includes('禁止访问目录')) {
        currentSection = 'forbidden_directories';
      } else if (trimmed.includes('严格模式')) {
        info.strict_mode = trimmed.includes('严格模式');
      } else if (trimmed.includes('最大文件大小')) {
        const match = trimmed.match(/(\d+\.?\d*)\s*MB/);
        if (match) {
          info.max_file_size_mb = parseFloat(match[1]);
        }
      } else if (trimmed.includes('最大读取行数')) {
        const match = trimmed.match(/(\d+)\s*行/);
        if (match) {
          info.max_read_lines = parseInt(match[1]);
        }
      } else if (trimmed.startsWith('📁') || trimmed.startsWith('📝') || 
                 trimmed.startsWith('🗂️') || trimmed.startsWith('⛔')) {
        const path = trimmed.replace(/^[📁📝🗂️⛔]\s*/, '');
        if (currentSection && info[currentSection as keyof FileSecurityInfo] && Array.isArray(info[currentSection as keyof FileSecurityInfo])) {
          (info[currentSection as keyof FileSecurityInfo] as string[]).push(path);
        }
      }
    });
    
    return info;
  };

  // 加载安全配置信息
  const loadSecurityInfo = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getFileSecurityInfo();
      if (response.success && response.data) {
        const parsedInfo = parseSecurityInfo(response.data);
        setSecurityInfo(parsedInfo as FileSecurityInfo);
      }
    } catch (error) {
      console.error('Failed to load file security info:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSecurityInfo();
  }, []);

  // 计算安全评分
  const calculateSecurityScore = (): number => {
    if (!securityInfo) return 0;
    
    let score = 0;
    // 基础配置检查
    if (securityInfo.readable_directories?.length > 0) score += 20;
    if (securityInfo.writable_directories?.length > 0) score += 20;
    if (securityInfo.deletable_directories?.length > 0) score += 15;
    if (securityInfo.forbidden_directories?.length > 0) score += 25;
    // 限制配置检查
    if (securityInfo.max_file_size_mb > 0 && securityInfo.max_file_size_mb <= 100) score += 10;
    if (securityInfo.max_read_lines > 0) score += 10;
    
    return Math.min(score, 100);
  };

  const securityScore = calculateSecurityScore();
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  const getSecurityLevel = (score: number) => {
    if (score >= 80) return { text: '高', color: 'success', icon: <CheckCircleOutlined /> };
    if (score >= 60) return { text: '中', color: 'warning', icon: <ExclamationCircleOutlined /> };
    return { text: '低', color: 'error', icon: <ExclamationCircleOutlined /> };
  };

  const securityLevel = getSecurityLevel(securityScore);

  if (compact) {
    return (
      <Card size="small" loading={loading}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Space>
              <SecurityScanOutlined style={{ color: currentTheme.token?.colorPrimary }} />
              <Text strong>文件安全</Text>
              <Badge 
                status={securityLevel.color as any} 
                text={`安全级别: ${securityLevel.text}`} 
              />
            </Space>
          </Col>
          <Col>
            <Button 
              size="small" 
              type="primary" 
              icon={<SettingOutlined />}
              onClick={() => navigate('/file-security')}
            >
              配置
            </Button>
          </Col>
        </Row>
      </Card>
    );
  }

  return (
    <Card 
      title={showTitle ? (
        <Space>
          <SecurityScanOutlined />
          <span>文件工具安全状态</span>
        </Space>
      ) : null}
      loading={loading}
      extra={
        <Space>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={loadSecurityInfo}
            size="small"
          />
          <Button 
            icon={<SettingOutlined />} 
            type="primary"
            onClick={() => navigate('/file-security')}
            size="small"
          >
            管理配置
          </Button>
        </Space>
      }
    >
      {securityInfo && (
        <>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Statistic
                title="安全评分"
                value={securityScore}
                suffix="/ 100"
                valueStyle={{ color: getScoreColor(securityScore) }}
                prefix={securityLevel.icon}
              />
              <Progress 
                percent={securityScore} 
                strokeColor={getScoreColor(securityScore)}
                size="small"
                showInfo={false}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="安全模式"
                value={securityInfo.strict_mode ? '严格' : '宽松'}
                valueStyle={{ 
                  color: securityInfo.strict_mode 
                    ? currentTheme.token?.colorError 
                    : currentTheme.token?.colorSuccess 
                }}
                prefix={securityInfo.strict_mode ? <LockOutlined /> : <UnlockOutlined />}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="配置目录"
                value={
                  (securityInfo.readable_directories?.length || 0) +
                  (securityInfo.writable_directories?.length || 0) +
                  (securityInfo.deletable_directories?.length || 0) +
                  (securityInfo.forbidden_directories?.length || 0)
                }
                prefix={<FolderOpenOutlined />}
              />
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Text strong>权限配置:</Text>
                <div>
                  <Tag color="blue">可读: {securityInfo.readable_directories?.length || 0}</Tag>
                  <Tag color="green">可写: {securityInfo.writable_directories?.length || 0}</Tag>
                  <Tag color="orange">可删: {securityInfo.deletable_directories?.length || 0}</Tag>
                  <Tag color="red">禁止: {securityInfo.forbidden_directories?.length || 0}</Tag>
                </div>
              </Space>
            </Col>
            <Col span={12}>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Text strong>限制配置:</Text>
                <div>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    文件大小: {securityInfo.max_file_size_mb}MB | 
                    读取行数: {securityInfo.max_read_lines}
                  </Text>
                </div>
              </Space>
            </Col>
          </Row>

          {securityScore < 60 && (
            <Alert
              message="安全提示"
              description="当前文件安全配置较为宽松，建议加强权限控制以提高系统安全性。"
              type="warning"
              showIcon
              style={{ marginTop: 16 }}
              action={
                <Button 
                  size="small" 
                  type="primary"
                  onClick={() => navigate('/file-security')}
                >
                  立即配置
                </Button>
              }
            />
          )}
        </>
      )}
    </Card>
  );
};

export default FileSecurityStatus;