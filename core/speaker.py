import threading
import pyttsx3

class Speaker:
    def __init__(self, rate=175, volume=1.0):
        self.engine=pyttsx3.init('sapi5')
        self.engine.setProperty('rate',rate); self.engine.setProperty('volume',volume)
        voices=self.engine.getProperty('voices') or []
        preferred=('zira','hazel','susan','samantha','female')
        for v in voices:
            n=(getattr(v,'name','') or '').lower()
            if any(x in n for x in preferred) and 'en' in (n+str(getattr(v,'languages','')).lower()):
                self.engine.setProperty('voice',v.id); break
        self.lock=threading.Lock()
    def say(self,text):
        def run():
            with self.lock:
                try:self.engine.say(text); self.engine.runAndWait()
                except Exception:pass
        threading.Thread(target=run,daemon=True).start()
