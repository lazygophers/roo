/**
 * 缓存工具配置模态框
 * 支持配置默认TTL、最大内存项、清理间隔等参数
 */

import React, { useState, useEffect } from 'react';
import {
  Alert,
  Space,
  Tooltip,
  Typography,
  Divider,
  Row,
  Col,
  Statistic,
  Card
} from 'antd';
import {
  ModalForm,
  ProFormDigit,
  ProFormSwitch,
  ProFormSelect
} from '@ant-design/pro-components';
import {
  InfoCircleOutlined,
  SettingOutlined,
  DatabaseOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { apiClient } from '../../api';

// const { Text, Title } = Typography;

export interface CacheToolsConfig {
  default_ttl: number;
  persistence_enabled: boolean;
  compression_enabled: boolean;
  stats_enabled: boolean;
}

interface CacheToolsConfigModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess?: () => void;
}

const CacheToolsConfigModal: React.FC<CacheToolsConfigModalProps> = ({
  visible,
  onCancel,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [cacheInfo, setCacheInfo] = useState<any>(null);

  // 获取缓存系统信息
  const loadCacheInfo = async () => {
    try {
      const response = await fetch('/api/cache/info');
      if (response.ok) {
        const data = await response.json();
        setCacheInfo(data);
      }
    } catch (error) {
      console.error('Failed to load cache info:', error);
    }
  };

  useEffect(() => {
    if (visible) {
      loadCacheInfo();
    }
  }, [visible]);

  // 请求初始配置数据
  const handleRequest = async () => {
    try {
      const response = await apiClient.getCategoryConfig('cache');
      if (response.success && response.data) {
        return response.data;
      }
      return {
        default_ttl: 3600,
        persistence_enabled: true,
        compression_enabled: false,
        stats_enabled: true
      };
    } catch (error) {
      console.error('Failed to load cache config:', error);
      return {
        default_ttl: 3600,
        persistence_enabled: true,
        compression_enabled: false,
        stats_enabled: true
      };
    }
  };

  // 保存配置
  const handleSave = async (values: CacheToolsConfig) => {
    try {
      setLoading(true);

      const response = await apiClient.updateCategoryConfigs('cache', values);

      if (response.success) {
        onSuccess?.();
        onCancel();
        return true;
      } else {
        throw new Error(response.message || '保存失败');
      }
    } catch (error) {
      console.error('Failed to save cache config:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // TTL选项
  const ttlOptions = [
    { label: '30秒', value: 30 },
    { label: '1分钟', value: 60 },
    { label: '5分钟', value: 300 },
    { label: '10分钟', value: 600 },
    { label: '30分钟', value: 1800 },
    { label: '1小时', value: 3600 },
    { label: '6小时', value: 21600 },
    { label: '12小时', value: 43200 },
    { label: '1天', value: 86400 }
  ];

  return (
    <ModalForm<CacheToolsConfig>
      title={
        <Space>
          <SettingOutlined />
          缓存工具配置
        </Space>
      }
      open={visible}
      onOpenChange={(open) => !open && onCancel()}
      modalProps={{
        destroyOnClose: true,
        width: 800
      }}
      submitter={{
        searchConfig: {
          submitText: '保存配置',
          resetText: '取消'
        },
        submitButtonProps: {
          loading
        }
      }}
      request={handleRequest}
      onFinish={handleSave}
    >
      <Alert
        message="缓存工具配置"
        description="配置Redis风格缓存工具的运行参数，包括默认TTL时间、内存限制和持久化选项。"
        type="info"
        icon={<InfoCircleOutlined />}
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* 系统状态展示 */}
      {cacheInfo && (
        <Card
          title={
            <Space>
              <DatabaseOutlined />
              缓存系统状态
            </Space>
          }
          size="small"
          style={{ marginBottom: 24 }}
        >
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="持久化缓存项"
                value={cacheInfo.persistent_items || 0}
                prefix={<DatabaseOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="总访问次数"
                value={cacheInfo.total_access_count || 0}
                prefix={<ClockCircleOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="系统状态"
                value={cacheInfo.status === 'active' ? '正常' : '异常'}
                valueStyle={{ color: cacheInfo.status === 'active' ? '#3f8600' : '#cf1322' }}
              />
            </Col>
          </Row>
        </Card>
      )}

      <Divider orientation="left">基础配置</Divider>

      <ProFormSelect
        name="default_ttl"
        label={
          <Space>
            <ClockCircleOutlined />
            默认TTL时间
            <Tooltip title="新建缓存项的默认生存时间，单位为秒">
              <InfoCircleOutlined />
            </Tooltip>
          </Space>
        }
        placeholder="请选择默认TTL时间"
        options={ttlOptions}
        fieldProps={{
          allowClear: false
        }}
        rules={[
          { required: true, message: '请选择默认TTL时间' }
        ]}
        extra="缓存项在指定时间后会自动过期删除，建议设置为3600秒（1小时）"
      />



      <Divider orientation="left">高级选项</Divider>

      <ProFormSwitch
        name="persistence_enabled"
        label={
          <Space>
            <DatabaseOutlined />
            启用持久化存储
            <Tooltip title="将缓存数据保存到数据库，重启后数据不会丢失">
              <InfoCircleOutlined />
            </Tooltip>
          </Space>
        }
        extra="启用后缓存数据会持久化到数据库，系统重启后不会丢失"
        checkedChildren="开启"
        unCheckedChildren="关闭"
      />

      <ProFormSwitch
        name="stats_enabled"
        label={
          <Space>
            <InfoCircleOutlined />
            启用统计功能
            <Tooltip title="收集访问统计、命中率等性能指标">
              <InfoCircleOutlined />
            </Tooltip>
          </Space>
        }
        extra="收集缓存访问统计信息，包括命中率、访问次数等"
        checkedChildren="开启"
        unCheckedChildren="关闭"
      />

      <ProFormSwitch
        name="compression_enabled"
        label={
          <Space>
            <DatabaseOutlined />
            启用数据压缩
            <Tooltip title="对大型缓存值进行压缩存储，节省存储空间">
              <InfoCircleOutlined />
            </Tooltip>
          </Space>
        }
        extra="对较大的缓存值进行压缩，可以节省存储空间但会增加CPU使用"
        checkedChildren="开启"
        unCheckedChildren="关闭"
      />

      <Alert
        message="配置说明"
        description={
          <div>
            <p><strong>默认TTL时间</strong>：建议设置为3600秒（1小时），平衡缓存效果和内存使用。</p>
            <p><strong>持久化存储</strong>：推荐开启，确保数据不会因重启而丢失。</p>
          </div>
        }
        type="warning"
        showIcon
        style={{ marginTop: 16 }}
      />
    </ModalForm>
  );
};

export default CacheToolsConfigModal;