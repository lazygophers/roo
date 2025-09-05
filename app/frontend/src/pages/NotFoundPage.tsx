import React from 'react';
import { Button, Result } from 'antd';
import { useNavigate } from 'react-router-dom';
import { HomeOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import styles from './NotFoundPage.module.css';

/**
 * 404页面组件
 * 处理未找到页面的情况，提供友好的错误提示和导航选项
 */
const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  /**
   * 返回首页
   */
  const handleGoHome = () => {
    navigate('/');
  };

  /**
   * 返回上一页
   */
  const handleGoBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <Result
          status='404'
          title={<span className={styles.title}>404</span>}
          subTitle={
            <div className={styles.subtitle}>
              <p className={styles.primaryText}>抱歉，您访问的页面不存在</p>
              <p className={styles.secondaryText}>页面可能已被移动、删除，或者您输入了错误的URL</p>
            </div>
          }
          extra={
            <div className={styles.actions}>
              <Button
                type='primary'
                icon={<HomeOutlined />}
                onClick={handleGoHome}
                className={styles.primaryButton}
                size='large'
              >
                返回首页
              </Button>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={handleGoBack}
                className={styles.secondaryButton}
                size='large'
              >
                返回上一页
              </Button>
            </div>
          }
          className={styles.result}
        />

        {/* 装饰性内容 */}
        <div className={styles.decoration}>
          <div className={styles.floatingElements}>
            <div className={`${styles.element} ${styles.element1}`} />
            <div className={`${styles.element} ${styles.element2}`} />
            <div className={`${styles.element} ${styles.element3}`} />
            <div className={`${styles.element} ${styles.element4}`} />
          </div>
        </div>

        {/* 帮助信息 */}
        <div className={styles.helpSection}>
          <h3 className={styles.helpTitle}>可能的解决方案：</h3>
          <ul className={styles.helpList}>
            <li className={styles.helpItem}>
              <span className={styles.helpIcon}>🔍</span>
              检查URL是否输入正确
            </li>
            <li className={styles.helpItem}>
              <span className={styles.helpIcon}>🔄</span>
              尝试刷新页面
            </li>
            <li className={styles.helpItem}>
              <span className={styles.helpIcon}>🏠</span>
              从首页重新导航
            </li>
            <li className={styles.helpItem}>
              <span className={styles.helpIcon}>🆘</span>
              联系管理员获取帮助
            </li>
          </ul>
        </div>

        {/* 快速链接 */}
        <div className={styles.quickLinks}>
          <h4 className={styles.quickLinksTitle}>快速导航</h4>
          <div className={styles.linkGrid}>
            <Button type='text' className={styles.quickLink} onClick={() => navigate('/')}>
              首页
            </Button>
            <Button type='text' className={styles.quickLink} onClick={() => navigate('/config')}>
              配置管理
            </Button>
            <Button type='text' className={styles.quickLink} onClick={() => navigate('/about')}>
              关于
            </Button>
          </div>
        </div>

        {/* 页脚信息 */}
        <div className={styles.footer}>
          <p className={styles.footerText}>如果问题持续存在，请联系技术支持</p>
          <p className={styles.footerSubtext}>错误代码：404 | 页面未找到</p>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
