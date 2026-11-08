const TOTAL_PAGES = 36;

export default function App() {
  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 14,
        background: '#111',
        color: '#f4ebdd',
        fontFamily: "'Source Han Sans SC','Microsoft YaHei',sans-serif",
      }}
    >
      <div style={{ fontSize: 13, letterSpacing: '.18em', color: '#f27314' }}>
        ZRH / PORTFOLIO 2026
      </div>
      <div style={{ fontSize: 22 }}>作品集共 {TOTAL_PAGES} 页</div>
      <a
        href="/index.html"
        style={{
          marginTop: 6,
          padding: '8px 18px',
          border: '1px solid #3a3a3a',
          borderRadius: 3,
          color: '#f4ebdd',
          fontSize: 13,
          textDecoration: 'none',
        }}
      >
        打开翻页预览器
      </a>
    </div>
  );
}
