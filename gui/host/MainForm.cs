using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;
using System.Diagnostics;
using System.Drawing;
using System.Windows.Forms;
using System.Net.Http;
using System.Threading.Tasks;

using System.Runtime.InteropServices;

namespace RedLightGUI;

public partial class MainForm : Form
{
    private WebView2 webView;
    private Process? backendProcess;
    
    [DllImport("dwmapi.dll", PreserveSig = true)]
    public static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);

    private const int DWMWA_USE_IMMERSIVE_DARK_MODE = 20;

    public MainForm()
    {
        InitializeComponent();
        
        // Enable Dark Mode for Title Bar
        int useImmersiveDarkMode = 1;
        DwmSetWindowAttribute(this.Handle, DWMWA_USE_IMMERSIVE_DARK_MODE, ref useImmersiveDarkMode, sizeof(int));
        
        // Restore standard window border so user has Close/Min/Max buttons
        this.FormBorderStyle = FormBorderStyle.Sizable;
        this.Text = "RedLight DL";
        this.StartPosition = FormStartPosition.CenterScreen;
        this.Size = new Size(1200, 800); // Set a reasonable default size
        this.BackColor = Color.Black; 
        
        InitializeWebView();
        StartBackend();
    }

    private void StartBackend()
    {
        try 
        {
            // Launch the bundled PyInstaller executable
            // Assumes "dist/RedLightServer/RedLightServer.exe" is adjacent to the app or known relative path
            string backendPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "RedLightServer", "RedLightServer.exe");
            
            // If running from VS Debug, we might need to look up a few folders or copying it there
            if (!File.Exists(backendPath))
            {
                // Fallback for dev environment: Look in project root dist
                // Path adjustment: bin\Debug\netX.0-windows (3 levels) -> host (4) -> gui (5) -> RedLightDL
                // Actually BaseDirectory is ...\gui\host\bin\Debug\net10.0-windows\
                // To get to RedLightDL root:
                // up 1: net10.0-windows
                // up 2: Debug
                // up 3: bin
                // up 4: host
                // up 5: gui
                // up 6: RedLightDL
                // So 5 or 6 levels depending on structure.
                
                string candidate = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, @"..\..\..\..\..\dist\RedLightServer\RedLightServer.exe"));
                if (File.Exists(candidate)) backendPath = candidate;
            }

            if (!File.Exists(backendPath))
            {
                MessageBox.Show($"Backend exe not found at: {backendPath}", "Setup Error");
                return;
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = backendPath,
                UseShellExecute = false,
                RedirectStandardOutput = true, // Hide console output again
                CreateNoWindow = true, // Hide console window
                WorkingDirectory = Path.GetDirectoryName(backendPath)
            };

            backendProcess = Process.Start(startInfo);
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Failed to start backend: {ex.Message}");
        }
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        if (backendProcess != null && !backendProcess.HasExited)
        {
            backendProcess.Kill();
        }
        base.OnFormClosing(e);
    }

    private async void InitializeWebView()
    {
        try
        {
            webView = new WebView2();
            webView.Dock = DockStyle.Fill;
            webView.DefaultBackgroundColor = Color.Transparent; 
            
            this.Controls.Add(webView);
    
            // Force no proxy to bypass VPN issues on localhost
            var options = new CoreWebView2EnvironmentOptions("--no-proxy-server");
            var env = await CoreWebView2Environment.CreateAsync(null, System.IO.Path.Combine(System.IO.Path.GetTempPath(), "RedLightGUI"), options);
            
            await webView.EnsureCoreWebView2Async(env);
            
            webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
            webView.CoreWebView2.Settings.AreDevToolsEnabled = true; // Keep enabled for debug
            webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
    
            webView.NavigationCompleted += (sender, args) =>
            {
                if (!args.IsSuccess)
                {
                    MessageBox.Show($"Navigation Failed: {args.WebErrorStatus}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            };

            // Wait for server to be ready
            bool isReady = await WaitForServer();
            if (isReady)
            {
                // Point to Python Backend (which serves React)
                webView.Source = new Uri("http://127.0.0.1:5000");
            }
            else
            {
                MessageBox.Show("Timed out waiting for backend server to start.", "Timeout Error");
            }
        }
        catch (Exception ex)
        {
             MessageBox.Show($"WebView Error: {ex.Message}\n{ex.StackTrace}", "Error");
        }
    }

    private async Task<bool> WaitForServer()
    {
        using (var client = new HttpClient())
        {
            // Try for 10 seconds
            for (int i = 0; i < 20; i++)
            {
                try
                {
                    var response = await client.GetAsync("http://127.0.0.1:5000/api/stats");
                    if (response.IsSuccessStatusCode)
                    {
                        return true;
                    }
                }
                catch
                {
                    // Ignore and retry
                }
                await Task.Delay(500);
            }
        }
        return false;
    }
}
