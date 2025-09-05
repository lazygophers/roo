import { Button, ConfigProvider, theme } from 'antd';
import styles from './App.module.css';

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
      }}
    >
      <div className={styles.container}>
        <Button type="primary">Primary Button</Button>
      </div>
    </ConfigProvider>
  );
}

export default App;