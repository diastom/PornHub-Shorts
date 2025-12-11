import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, Settings, Activity, Zap, Play, Search, X, List, Globe, MoreHorizontal, Save, Folder, Clock } from 'lucide-react';
import AnimatedButton from './components/AnimatedButton';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [url, setUrl] = useState('');
  const [stats, setStats] = useState({ total_downloads: 0, total_size: 0, avg_quality: 0 });

  // Mock Config State
  const [config, setConfig] = useState({
    downloadPath: 'C:\\Downloads\\RedLight',
    maxConcurrent: 3,
    quality: '1080p',
    theme: 'dark'
  });

  // Fetch Stats on Mount & Periodically
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('/api/stats');
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (e) {
        console.error("API Error:", e);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStartDownload = async () => {
    if (!url) return;
    try {
      const res = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (data.success) {
        console.log("Download Started:", data.id);
        setActiveTab('downloads');
        setUrl('');
      }
    } catch (e) {
      console.error("Download Failed:", e);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <nav className="sidebar">
        <div className="logo-area">
          <Zap size={28} color="var(--accent-color)" />
          <span className="logo-text">RedLight<span className="logo-suffix">DL</span></span>
        </div>

        <div className="nav-links">
          <NavButton icon={<Activity />} label="Dashboard" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <NavButton icon={<Globe />} label="Search" active={activeTab === 'search'} onClick={() => setActiveTab('search')} />
          <NavButton icon={<List />} label="Playlist" active={activeTab === 'playlist'} onClick={() => setActiveTab('playlist')} />
          <NavButton icon={<Download />} label="Downloads" active={activeTab === 'downloads'} onClick={() => setActiveTab('downloads')} />
          <NavButton icon={<Clock />} label="History" active={activeTab === 'history'} onClick={() => setActiveTab('history')} />
          <NavButton icon={<MoreHorizontal />} label="Extras" active={activeTab === 'extras'} onClick={() => setActiveTab('extras')} />
          <div className="spacer" style={{ flex: 1 }} />
          <NavButton icon={<Settings />} label="Settings" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        <header className="top-bar">
          <div className="search-bar">
            {/* Changing icon based on context if needed, keeping generic for now */}
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder={activeTab === 'playlist' ? "Paste Playlist URL..." : "Paste URL to download..."}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            {url && (
              <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="clear-btn"
                onClick={() => setUrl('')}
              >
                <X size={14} />
              </motion.button>
            )}
          </div>
          <AnimatedButton variant="primary" onClick={handleStartDownload}>
            <Play size={18} fill="currentColor" /> {activeTab === 'playlist' ? 'Fetch List' : 'Start'}
          </AnimatedButton>
        </header>

        <div className="content-area">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="tab-content"
              style={{ height: '100%' }}
            >
              {activeTab === 'dashboard' && <DashboardView stats={stats} />}
              {activeTab === 'search' && <SearchView />}
              {activeTab === 'playlist' && <PlaylistView />}
              {activeTab === 'downloads' && <DownloadsView />}
              {activeTab === 'history' && <HistoryView />}
              {activeTab === 'extras' && <ExtrasView />}
              {activeTab === 'settings' && <SettingsView config={config} setConfig={setConfig} />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

const NavButton = ({ icon, label, active, onClick }) => (
  <motion.div
    className={`nav-btn ${active ? 'active' : ''}`}
    onClick={onClick}
    whileHover={{ x: 5, backgroundColor: 'rgba(255,255,255,0.05)' }}
    whileTap={{ scale: 0.98 }}
  >
    {icon}
    <span>{label}</span>
    {active && (
      <motion.div
        className="active-indicator"
        layoutId="activeTab"
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      />
    )}
  </motion.div>
);

const DashboardView = ({ stats }) => (
  <div className="view-container">
    <h1 className="hero-title">Ready to <span className="highlight">Accelerate?</span></h1>
    <p className="hero-subtitle">Paste a link above to start downloading securely and anonymously.</p>

    <div className="stats-grid">
      <StatCard label="Total Downloads" value={stats.total_downloads || 0} />
      <StatCard label="Total Size" value={formatBytes(stats.total_size || 0)} />
      <StatCard label="Avg Quality" value={`${stats.avg_quality || 0}p`} />
    </div>
  </div>
);

function formatBytes(bytes, decimals = 2) {
  if (!+bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

const SearchView = () => (
  <div className="view-container">
    <h2>Search Engine</h2>
    <p className="text-secondary">Browse supported sites directly.</p>
    <div className="placeholder-box">
      <Globe size={48} className="text-secondary" />
      <p>Site Browser Implementation Pending</p>
    </div>
  </div>
);

const PlaylistView = () => (
  <div className="view-container">
    <h2>Playlist Downloader</h2>
    <p className="text-secondary">Batch process entire series or playlists.</p>
    <div className="placeholder-box">
      <List size={48} className="text-secondary" />
      <p>Queue Manager Implementation Pending</p>
    </div>
  </div>
);

const DownloadsView = () => <div className="placeholder-view"><h2>Downloads History</h2><p>No active downloads.</p></div>;
const ExtrasView = () => <div className="placeholder-view"><h2>Extras</h2><p>Converters, Metadata Editors, etc.</p></div>;

const SettingsView = ({ config, setConfig }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="view-container settings-view">
      <h2>Configuration</h2>
      <div className="settings-grid">
        <div className="setting-item">
          <label>Download Path</label>
          <div className="input-with-icon">
            <Folder size={18} />
            <input type="text" name="downloadPath" value={config.downloadPath} onChange={handleChange} />
          </div>
        </div>

        <div className="setting-item">
          <label>Max Concurrent Downloads</label>
          <select name="maxConcurrent" value={config.maxConcurrent} onChange={handleChange}>
            <option value="1">1</option>
            <option value="3">3</option>
            <option value="5">5</option>
            <option value="10">Unlimited</option>
          </select>
        </div>

        <div className="setting-item">
          <label>Default Quality</label>
          <select name="quality" value={config.quality} onChange={handleChange}>
            <option value="4k">4K Ultra HD</option>
            <option value="1080p">1080p Full HD</option>
            <option value="720p">720p HD</option>
            <option value="480p">480p SD</option>
          </select>
        </div>

        <div className="setting-item">
          <label>Theme</label>
          <select name="theme" value={config.theme} onChange={handleChange}>
            <option value="dark">Cyberpunk Dark</option>
            <option value="light">Light (Experimental)</option>
          </select>
        </div>
      </div>

      <div className="settings-actions">
        <AnimatedButton variant="primary">
          <Save size={18} /> Save Config
        </AnimatedButton>
      </div>
    </div>
  );
};

const StatCard = ({ label, value }) => (
  <motion.div
    className="stat-card"
    whileHover={{ y: -5, borderColor: 'var(--accent-color)' }}
  >
    <h3>{value}</h3>
    <p>{label}</p>
  </motion.div>
);

const HistoryView = () => {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch('/api/downloads/history?limit=50')
      .then(res => res.json())
      .then(data => setHistory(data))
      .catch(console.error);
  }, []);

  return (
    <div className="view-container">
      <h2>Download History</h2>
      <div className="history-list">
        {history.length === 0 ? (
          <p className="empty-state">No downloads yet.</p>
        ) : (
          <table className="history-table" style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>Date</th>
                <th style={{ padding: '10px' }}>Title</th>
                <th style={{ padding: '10px' }}>Quality</th>
                <th style={{ padding: '10px' }}>Site</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '10px', color: '#888' }}>{new Date(item.date_downloaded).toLocaleDateString()}</td>
                  <td style={{ padding: '10px' }}>{item.title || item.filename}</td>
                  <td style={{ padding: '10px', color: 'var(--accent-color)' }}>{item.quality}p</td>
                  <td style={{ padding: '10px', textTransform: 'capitalize' }}>{item.site || 'Unknown'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default App;
