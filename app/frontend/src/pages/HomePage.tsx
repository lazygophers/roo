import React from 'react';
import { Typography, Card, Space } from 'antd';
import styles from './HomePage.module.css';

const { Title, Paragraph } = Typography;

/**
 * 首页组件
 * 展示应用的基本信息和欢迎界面
 */
const HomePage: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.hero}>
        <Title level={1} className={styles.title}>
          欢迎使用 Roo Code 配置管理系统
        </Title>
        <Paragraph className={styles.subtitle}>
          一个强大而灵活的代码配置管理平台，帮助您轻松管理和组织项目配置。
        </Paragraph>
      </div>

      <div className={styles.features}>
        <Space size='large' wrap>
          <Card hoverable className={styles.featureCard} title='配置管理' size='small'>
            <p>集中管理所有项目配置，支持版本控制和历史追溯。</p>
          </Card>

          <Card hoverable className={styles.featureCard} title='规则组合' size='small'>
            <p>灵活组合各种规则配置，适应不同项目需求。</p>
          </Card>

          <Card hoverable className={styles.featureCard} title='实时预览' size='small'>
            <p>实时预览配置效果，所见即所得的配置体验。</p>
          </Card>
        </Space>
      </div>
    </div>
  );
};

export default HomePage;
