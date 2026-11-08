import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// 作品集本体是静态的 index.html（翻页预览器 + 36 页独立 SVG），不依赖 React 渲染。
// 这里只在页面里真的存在 #root 容器时才挂载，避免把静态页面顶掉。
const root = document.getElementById('root');

if (root) {
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
}
