import datetime,re,subprocess,pyautogui,os
from pathlib import Path
from urllib.parse import quote_plus

class CommandEngine:
    def __init__(self,config,launcher,speaker=None,log=None,status=None,brain=None):
        self.config=config;self.launcher=launcher;self.speaker=speaker;self.log=log or (lambda *_:None);self.status=status or (lambda *_:None);self.brain=brain;self.running=True
    def reply(self,msg):self.log('MAYA',msg); self.speaker and self.speaker.say(msg)
    def clean(self,text):
        low=text.lower().strip(); variants=[self.config.get('wake_phrase','hey maya'), 'heymaya','hey maya','hey maia','maya']
        for v in sorted(set(variants),key=len,reverse=True):
            if low.startswith(v):return text[len(v):].strip(' ,:;-')
        return text
    def handle(self,raw):
        text=self.clean(raw.strip());
        if not text:return
        self.log('YOU',text);self.status('THINKING');low=text.lower().strip(' .!?')
        try:
            if low in ('stop','stop listening','go to sleep','sleep'):self.reply('Going to sleep.');self.running=False;return
            if low in ('hello','hi','hello maya','hi maya'):self.reply('Hello. How can I help you?');return
            if low in ('time','what time is it','what is the time'):self.reply(datetime.datetime.now().strftime('It is %I:%M %p.'));return
            if low in ('date','what date is it','what is today','what is todays date'):self.reply(datetime.datetime.now().strftime('Today is %A, %d %B %Y.'));return
            m=re.match(r'^(?:open|launch|start|go to|show me|take me to|navigate to|bring up|pull up|visit)\s+(.+)$',text,re.I)
            if m:
                target=re.sub(r'\bplease$','',m.group(1).strip(),flags=re.I).strip();self.log('ACTION','Resolving: '+target);ok=self.launcher.open_anything(target);self.reply(f'Opening {target}.' if ok else f'I could not find or open {target}.');return
            m=re.match(r'^(?:close|quit|exit)\s+(.+)$',text,re.I)
            if m:
                target=m.group(1).strip();ok=self.launcher.close_app(target);self.reply(f'Closing {target}.' if ok else f'I could not close {target}.');return
            m=re.match(r'^(?:search youtube for|search youtube|youtube search|find on youtube|play on youtube)\s+(.+)$',text,re.I)
            if m:
                q=m.group(1).strip();self.launcher.youtube_search(q);self.reply(f'Searching YouTube for {q}.');return
            m=re.match(r'^(?:search|google|look up|find)\s+(?:for\s+)?(.+)$',text,re.I)
            if m:
                q=m.group(1).strip();self.launcher.google_search(q);self.reply(f'Searching for {q}.');return
            m=re.match(r'^(?:play|listen to)\s+(.+)$',text,re.I)
            if m:
                q=m.group(1).strip();self.launcher.youtube_search(q);self.reply(f'Opening {q} on YouTube.');return
            m=re.match(r'^(?:type|write|enter)\s+(.+)$',text,re.I)
            if m:pyautogui.write(m.group(1),interval=.008);self.reply('Typing it now.');return
            if low in ('volume up','increase volume','turn volume up','louder'):pyautogui.press('volumeup', presses=4);self.reply('Volume increased.');return
            if low in ('volume down','decrease volume','turn volume down','quieter'):pyautogui.press('volumedown', presses=4);self.reply('Volume decreased.');return
            if low in ('mute','mute volume','turn volume off'):pyautogui.press('volumemute');self.reply('Muted.');return
            if low in ('play pause','pause','resume','play music'):pyautogui.press('playpause');self.reply('Media control sent.');return
            if low in ('next','next song','next track'):pyautogui.press('nexttrack');self.reply('Next track.');return
            if low in ('previous','previous song','previous track'):pyautogui.press('prevtrack');self.reply('Previous track.');return
            if low in ('show desktop','minimize everything'):pyautogui.hotkey('win','d');self.reply('Showing the desktop.');return
            if low in ('switch window','next window','switch app'):pyautogui.hotkey('alt','tab');self.reply('Switching window.');return
            if low in ('take screenshot','screenshot','capture screen'):pyautogui.hotkey('win','shift','s');self.reply('Screenshot tool opened.');return
            if low in ('copy','copy that'):pyautogui.hotkey('ctrl','c');self.reply('Copied.');return
            if low in ('paste','paste that'):pyautogui.hotkey('ctrl','v');self.reply('Pasted.');return
            if low in ('open clipboard','clipboard'):pyautogui.hotkey('win','v');self.reply('Opening clipboard history.');return
            if low in ('open settings','windows settings'):self.launcher.open_anything('settings');self.reply('Opening Windows Settings.');return
            if low in ('lock computer','lock pc','lock my pc'):subprocess.Popen(['rundll32.exe','user32.dll,LockWorkStation']);return
            if low in ('cancel shutdown','abort shutdown'):subprocess.Popen(['shutdown','/a']);self.reply('Shutdown cancelled.');return
            if low in ('restart computer','restart pc','shutdown computer','shutdown pc','turn off computer'):
                self.reply('For safety, use the Windows confirmation command from the console for restart or shutdown.');return
            if self.brain:
                ans=self.brain.ask('You are MAYA, a concise Windows desktop assistant. Explain briefly what the user wants, but do not execute commands. User: '+text)
                if ans:self.reply(ans);return
            self.launcher.google_search(text);self.reply(f'I searched the web for {text}.')
        except Exception as e:self.log('ERROR',str(e));self.reply('I ran into an error while executing that command.')
        finally:self.status('READY')
