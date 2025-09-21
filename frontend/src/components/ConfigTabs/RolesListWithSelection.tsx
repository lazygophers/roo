import React, { useState, useCallback, useEffect } from 'react';
import { Card, List, Button, Typography, Tag, Space, message, Empty, Tooltip, Spin, theme } from 'antd';
import { UserOutlined, CheckOutlined } from '@ant-design/icons';
import { apiClient, RoleInfo } from '../../api';
import { SelectedItem } from '../../types/selection';
import { useLazyLoading } from '../../hooks/useLazyLoading';

const { Text, Paragraph } = Typography;

interface RolesListWithSelectionProps {
  selectedItems: SelectedItem[];
  onToggleSelection: (item: SelectedItem) => void;
  onSelectAll: (items: SelectedItem[]) => void;
  onClearSelection: () => void;
}

const RolesListWithSelection: React.FC<RolesListWithSelectionProps> = ({
  selectedItems,
  onToggleSelection,
  onSelectAll,
  onClearSelection
}) => {
  const { token } = theme.useToken();
  const [roles, setRoles] = useState<RoleInfo[]>([]);

  // 惰性加载角色数据
  const loadRolesData = useCallback(async () => {
    try {
      console.log('[RolesList] Starting to load roles data...');
      const response = await apiClient.getRoles();
      setRoles(response.data);
      console.log(`[RolesList] Loaded ${response.data.length} roles`);
    } catch (error) {
      console.error('Failed to load roles:', error);
      message.error('加载角色失败');
      throw error; // 重新抛出错误以便useLazyLoading处理
    }
  }, []);

  const {
    loading,
    loaded,
    error,
    load: triggerLoad
  } = useLazyLoading(loadRolesData, {
    key: 'roles-list',
    autoLoad: false, // 改为手动加载
    cacheTime: 5 * 60 * 1000 // 5分钟缓存
  });

  // 当组件首次挂载时触发加载
  useEffect(() => {
    if (!loaded && !loading) {
      console.log('[RolesList] Component mounted, triggering load...');
      triggerLoad();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // 检查角色是否已选择
  const isRoleSelected = (roleId: string) => {
    return selectedItems.some(item => item.type === 'role' && item.id === roleId);
  };

  // 获取已选择的角色数量
  const selectedRoleCount = selectedItems.filter(item => item.type === 'role').length;

  // 转换角色为选择项
  const convertRoleToSelectedItem = (role: RoleInfo): SelectedItem => ({
    id: role.name,
    type: 'role',
    name: role.title,
    data: role
  });

  // 清空角色选择
  const handleClearRoleSelection = () => {
    // 只移除角色类型的选择，保留其他类型
    const nonRoleItems = selectedItems.filter(item => item.type !== 'role');
    onClearSelection();
    // 如果有非角色项目，重新添加它们
    if (nonRoleItems.length > 0) {
      onSelectAll(nonRoleItems);
    }
  };

  // 切换角色选择
  const handleToggleRole = (role: RoleInfo) => {
    const selectedItem = convertRoleToSelectedItem(role);
    onToggleSelection(selectedItem);
  };

  // 处理加载状态
  if (loading && !loaded) {
    return (
      <div style={{
        height: '400px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Spin size="large" />
        <span style={{ marginLeft: 12, color: token.colorTextSecondary }}>
          正在加载角色数据...
        </span>
      </div>
    );
  }

  // 处理错误状态
  if (error) {
    return (
      <div style={{
        height: '400px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: token.colorTextSecondary
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>❌</div>
        <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
          加载角色数据失败
        </div>
        <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '16px' }}>
          {error.message || '未知错误'}
        </div>
        <Button type="primary" onClick={triggerLoad}>
          重新加载
        </Button>
      </div>
    );
  }

  return (
    <Card
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>
            <UserOutlined style={{ marginRight: 8 }} />
            角色列表 ({selectedRoleCount}/{roles.length})
          </span>
          <Space>
            <Button 
              size="small" 
              onClick={handleClearRoleSelection}
              disabled={selectedRoleCount === 0}
            >
              清空
            </Button>
          </Space>
        </div>
      }
      styles={{ body: { padding: '12px' } }}
    >
      {roles.length === 0 ? (
        <Empty 
          description="暂无角色" 
          style={{ margin: '40px 0' }} 
        />
      ) : (
        <List
          dataSource={roles}
          renderItem={(role) => {
            const isSelected = isRoleSelected(role.name);
            
            return (
              <List.Item
                style={{
                  padding: '12px',
                  backgroundColor: isSelected ? 'rgba(24, 144, 255, 0.05)' : 'transparent',
                  border: isSelected ? '1px solid rgba(24, 144, 255, 0.2)' : '1px solid transparent',
                  borderRadius: '4px',
                  marginBottom: '8px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onClick={() => handleToggleRole(role)}
              >
                <List.Item.Meta
                  avatar={
                    <div style={{
                      width: 36,
                      height: 36,
                      borderRadius: '4px',
                      backgroundColor: isSelected ? '#1890ff' : '#f5f5f5',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: isSelected ? '#fff' : '#999'
                    }}>
                      {isSelected ? <CheckOutlined /> : <UserOutlined />}
                    </div>
                  }
                  title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Text strong style={{ color: isSelected ? '#52c41a' : undefined }}>
                        {role.title}
                      </Text>
                      <Tag color="blue" style={{ fontSize: '10px' }}>
                        {role.category}
                      </Tag>
                    </div>
                  }
                  description={
                    <div>
                      <Paragraph 
                        ellipsis={{ rows: 2, expandable: false }} 
                        style={{ margin: '4px 0', fontSize: '12px' }}
                      >
                        {role.description}
                      </Paragraph>
                      
                      {/* 特征标签 */}
                      <div style={{ marginTop: 8 }}>
                        <Text type="secondary" style={{ fontSize: '11px', marginRight: 8 }}>
                          特征:
                        </Text>
                        {role.traits.map((trait, index) => (
                          <Tag 
                            key={index} 
                            color="geekblue"
                            style={{ fontSize: '10px', margin: '1px' }}
                          >
                            {trait}
                          </Tag>
                        ))}
                      </div>
                      
                      {/* 功能特性 */}
                      {role.features.length > 0 && (
                        <div style={{ marginTop: 4 }}>
                          <Text type="secondary" style={{ fontSize: '11px', marginRight: 8 }}>
                            功能:
                          </Text>
                          <Tooltip 
                            title={
                              <div>
                                {role.features.map((feature, index) => (
                                  <div key={index} style={{ marginBottom: 4 }}>
                                    • {feature}
                                  </div>
                                ))}
                              </div>
                            }
                          >
                            <Tag 
                              color="green"
                              style={{ fontSize: '10px' }}
                            >
                              {role.features.length} 项功能
                            </Tag>
                          </Tooltip>
                        </div>
                      )}
                      
                      {/* 限制说明 */}
                      {role.restrictions && role.restrictions.length > 0 && (
                        <div style={{ marginTop: 4 }}>
                          <Text type="secondary" style={{ fontSize: '11px', marginRight: 8 }}>
                            限制:
                          </Text>
                          <Tooltip 
                            title={
                              <div>
                                {role.restrictions.map((restriction, index) => (
                                  <div key={index} style={{ marginBottom: 4 }}>
                                    • {restriction}
                                  </div>
                                ))}
                              </div>
                            }
                          >
                            <Tag 
                              color="orange"
                              style={{ fontSize: '10px' }}
                            >
                              有使用限制
                            </Tag>
                          </Tooltip>
                        </div>
                      )}
                    </div>
                  }
                />
              </List.Item>
            );
          }}
        />
      )}
      
      <div style={{ 
        textAlign: 'center', 
        marginTop: 16, 
        paddingTop: 16, 
        borderTop: '1px solid #f0f0f0',
        color: '#666',
        fontSize: '12px'
      }}>
        角色配置是可选的，单选模式，可随时取消选择
      </div>
    </Card>
  );
};

export default RolesListWithSelection;