import requests
class Brain:
    def __init__(self,config):
        self.enabled=bool(config.get('ollama_enabled',False)); self.url=config.get('ollama_url','http://127.0.0.1:11434').rstrip('/'); self.model=config.get('ollama_model','llama3:8b')
    def ask(self,prompt):
        if not self.enabled:return ''
        try:
            r=requests.post(self.url+'/api/generate',json={'model':self.model,'prompt':prompt,'stream':False},timeout=12); r.raise_for_status(); return r.json().get('response','').strip()
        except Exception:return ''
