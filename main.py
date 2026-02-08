import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import webbrowser

# Import existing Flask app
from app import app as flask_app

class FlaskThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        # Run Flask app on port 5000
        flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

class MainApp(App):
    def build(self):
        # Start Flask in a separate thread
        self.flask_thread = FlaskThread()
        self.flask_thread.start()
        
        # Simple UI to launch browser
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        label = Label(text="ETF 动量策略服务正在运行...", size_hint_y=0.2)
        layout.add_widget(label)
        
        # In Android, opening a browser is safer/easier than embedding WebView directly without specific permissions/plugins
        # However, for a "native app feel", usually we want a WebView.
        # But standard Kivy doesn't have a WebView widget built-in easily without jnius/android specific code.
        # For simplicity and reliability, we will launch the system browser.
        
        # Alternatively, we can use `kivy-garden.webview` or `android.run_on_ui_thread` if we want embedded.
        # For this first version, let's try to just open the URL.
        
        Clock.schedule_once(self.open_browser, 3) # Open after 3 seconds to let Flask start
        
        return layout

    def open_browser(self, dt):
        webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    MainApp().run()
