import os,re,subprocess,webbrowser,shutil
from pathlib import Path
from urllib.parse import quote_plus

class WindowsLauncher:
    def __init__(self,config,status=None): self.config=config; self.status=status or (lambda *_:None)
    def _start(self,target):
        try: os.startfile(str(target)); return True
        except Exception:
            try: subprocess.Popen([str(target)], shell=False); return True
            except Exception:
                try: subprocess.Popen(str(target), shell=True); return True
                except Exception: return False
    def open_url(self,url):
        try: return bool(webbrowser.open(url,new=2))
        except Exception:
            try: os.startfile(url); return True
            except Exception: return False
    def ps(self,cmd,timeout=6):
        try:
            r=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-Command',cmd],capture_output=True,text=True,timeout=timeout,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            return r.stdout.strip()
        except Exception: return ''
    def _start_menu(self,name):
        safe=name.replace("'","''")
        app=self.ps(f"Get-StartApps | Where-Object {{$_.Name -like '*{safe}*'}} | Select-Object -First 1 -ExpandProperty AppID")
        if app:
            try: subprocess.Popen(['explorer.exe',f'shell:AppsFolder\\{app.splitlines()[0].strip()}']); return True
            except Exception: pass
        roots=[Path(os.environ.get('APPDATA',''))/'Microsoft/Windows/Start Menu/Programs',Path(os.environ.get('PROGRAMDATA',''))/'Microsoft/Windows/Start Menu/Programs']
        n=name.lower().strip()
        for root in roots:
            if root.exists():
                try:
                    for p in root.rglob('*'):
                        if p.is_file() and p.suffix.lower() in ('.lnk','.url') and n in p.stem.lower(): return self._start(p)
                except Exception: pass
        return False
    def _common(self,n):
        L=Path(os.environ.get('LOCALAPPDATA','')); P=Path(os.environ.get('PROGRAMFILES','C:/Program Files')); P86=Path(os.environ.get('PROGRAMFILES(X86)','C:/Program Files (x86)')); W=Path(os.environ.get('WINDIR','C:/Windows'))
        return {'chrome':[L/'Google/Chrome/Application/chrome.exe',P/'Google/Chrome/Application/chrome.exe',P86/'Google/Chrome/Application/chrome.exe'],
        'edge':[P/'Microsoft/Edge/Application/msedge.exe',P86/'Microsoft/Edge/Application/msedge.exe'],
        'vs code':[L/'Programs/Microsoft VS Code/Code.exe',P/'Microsoft VS Code/Code.exe',P86/'Microsoft VS Code/Code.exe'],
        'visual studio code':[L/'Programs/Microsoft VS Code/Code.exe',P/'Microsoft VS Code/Code.exe',P86/'Microsoft VS Code/Code.exe'],
        'notepad':[W/'System32/notepad.exe'],'calculator':[W/'System32/calc.exe'],'calc':[W/'System32/calc.exe'],
        'paint':[W/'System32/mspaint.exe'],'file explorer':[W/'explorer.exe'],'explorer':[W/'explorer.exe'],
        'task manager':[W/'System32/Taskmgr.exe'],'cmd':[W/'System32/cmd.exe'],'command prompt':[W/'System32/cmd.exe'],
        'powershell':[W/'System32/WindowsPowerShell/v1.0/powershell.exe'],'terminal':[W/'System32/WindowsPowerShell/v1.0/powershell.exe']}.get(n,[])
    def open_app(self,name):
        key=name.lower().strip(); target=self.config.get('app_aliases',{}).get(key,key)
        if ':' in target and not re.match(r'^[A-Za-z]:[\\/]',target):
            try: os.startfile(target); return True
            except Exception: pass
        for exe in (target,target+'.exe'):
            try:
                found=shutil.which(exe)
                if found and self._start(found): return True
                r=subprocess.run(['where.exe',exe],capture_output=True,text=True,timeout=3,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                if r.returncode==0 and r.stdout.strip() and self._start(r.stdout.splitlines()[0]): return True
            except Exception: pass
        for p in self._common(key):
            if p.exists() and self._start(p): return True
        return self._start_menu(key)
    def open_anything(self,target):
        target=target.strip().strip('"\''); target=re.sub(r'^(?:the|my)\s+','',target,flags=re.I); low=target.lower().strip()
        if re.match(r'^https?://',target,re.I): return self.open_url(target)
        if low.startswith('www.') or re.match(r'^[\w.-]+\.[a-z]{2,}(/.*)?$',target,re.I): return self.open_url('https://'+target)
        home=Path.home(); folders={'downloads':home/'Downloads','download':home/'Downloads','desktop':home/'Desktop','documents':home/'Documents','pictures':home/'Pictures','videos':home/'Videos','music':home/'Music','this pc':'shell:MyComputerFolder','recycle bin':'shell:RecycleBinFolder'}
        if low in folders:
            try: os.startfile(str(folders[low])); return True
            except Exception: pass
        if Path(target).exists() and self._start(target): return True
        sites=self.config.get('websites',{})
        if low in sites and self.open_url(sites[low]): return True
        if self.open_app(target): return True
        return False
    def close_app(self,name):
        target=self.config.get('app_aliases',{}).get(name.lower().strip(),name.lower().strip()).replace('.exe','')
        if ':' in target: return False
        try:
            r=subprocess.run(['taskkill','/IM',target+'.exe','/F'],capture_output=True,text=True,timeout=5,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)); return r.returncode==0
        except Exception: return False
    def google_search(self,q): return self.open_url('https://www.google.com/search?q='+quote_plus(q))
    def youtube_search(self,q): return self.open_url('https://www.youtube.com/results?search_query='+quote_plus(q))
