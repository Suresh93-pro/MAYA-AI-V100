import math, random, threading, time, tkinter as tk
try: import psutil
except Exception: psutil=None
from core.config import load_config
from core.speaker import Speaker
from core.listener import Listener
from core.launcher import WindowsLauncher
from core.brain import Brain
from core.commands import CommandEngine

BG='#02050b'; PANEL='#06121d'; PANEL2='#071a27'; CYAN='#63f7ff'; BLUE='#168cff'; WHITE='#e9feff'; MUTED='#55798b'; GREEN='#43ffad'; PURPLE='#b878ff'; ORANGE='#ffc45b'; RED='#ff5d78'; GRID='#0b2634'

class MayaApp:
    def __init__(self):
        self.cfg=load_config(); self.running=True; self.frame=0; self.wave=0; self.mode='BOOTING'; self.start_time=time.time(); self.logs=[]
        self.root=tk.Tk(); self.root.title('MAYA AI // V100 FINAL NEURAL DESKTOP'); self.root.geometry('1600x920'); self.root.minsize(1180,760); self.root.configure(bg=BG)
        try:self.root.state('zoomed')
        except:pass
        self.speaker=Speaker(self.cfg['voice_rate'],self.cfg['voice_volume']); self.launcher=WindowsLauncher(self.cfg,self.set_status); self.brain=Brain(self.cfg)
        self.engine=CommandEngine(self.cfg,self.launcher,self.speaker,self.add_log,self.set_status,self.brain)
        self.listener=Listener(self.cfg['language'],self.cfg['listen_timeout'],self.cfg['phrase_time_limit'],self.set_status)
        self.build(); self.root.protocol('WM_DELETE_WINDOW',self.close); self.root.bind('<Escape>',lambda e:self.close()); self.root.bind('<F9>',lambda e:self.toggle_voice()); self.root.after(600,self.start_voice); self.animate()
    def build(self):
        self.bg=tk.Canvas(self.root,bg=BG,highlightthickness=0); self.bg.pack(fill='both',expand=True); self.bg.bind('<Configure>',lambda e:self.draw())
        # top HUD
        self.bg.create_text(34,27,anchor='w',text='MAYA',fill=WHITE,font=('Segoe UI',31,'bold'),tags='static')
        self.bg.create_text(37,61,anchor='w',text='V100  //  FINAL NEURAL DESKTOP  •  VOICE  •  AUTOMATION  •  AI',fill=MUTED,font=('Consolas',9,'bold'),tags='static')
        self.bg.create_text(1562,28,anchor='e',text='NEURAL CORE // 100',fill=CYAN,font=('Consolas',10,'bold'),tags='static')
        self.dot=self.bg.create_oval(1475,22,1487,34,fill=GREEN,outline='',tags='static'); self.bg.create_text(1495,28,anchor='w',text='ONLINE',fill=GREEN,font=('Consolas',9,'bold'),tags='static')
        self.build_panels()
    def panel(self,x,y,w,h,title,sub):
        self.bg.create_rectangle(x,y,x+w,y+h,fill=PANEL,outline='#123447',width=1,tags='static')
        self.bg.create_line(x,y+1,x+w*.36,y+1,fill=CYAN,width=2,tags='static')
        self.bg.create_text(x+16,y+17,anchor='w',text=title,fill=CYAN,font=('Consolas',10,'bold'),tags='static')
        self.bg.create_text(x+16,y+34,anchor='w',text=sub,fill=MUTED,font=('Consolas',7),tags='static')
    def build_panels(self):
        self.panel(22,110,286,610,'SYSTEM TELEMETRY','LIVE // HARDWARE + CORE')
        self.panel(1292,110,286,610,'COMMAND STREAM','LIVE // EXECUTION FEED')
        self.panel(22,735,1556,118,'CAPABILITY MATRIX','VOICE-READY // V100')
        self.stats=[]
        for i,n in enumerate(['VOICE CHANNEL','COMMAND ENGINE','WINDOWS LINK','WEB LINK','AI BRAIN']):
            y=165+i*46; self.bg.create_text(42,y,anchor='w',text='● '+n,fill=GREEN,font=('Consolas',9,'bold'),tags='static'); self.stats.append(self.bg.create_text(270,y,anchor='e',text='READY',fill=GREEN,font=('Consolas',8,'bold'),tags='static'))
        self.bg.create_text(42,410,anchor='w',text='SKILLS',fill=PURPLE,font=('Consolas',9,'bold'),tags='static')
        skills=['ANY APP / URL','FILES + FOLDERS','SEARCH + YOUTUBE','WINDOW CONTROL','VOICE TYPING','MEDIA + VOLUME','WINDOWS SYSTEM','LOCAL OLLAMA']
        for i,s in enumerate(skills): self.bg.create_text(44,438+i*24,anchor='w',text='◆ '+s,fill='#7898a6',font=('Consolas',8),tags='static')
        self.bg.create_text(1310,165,anchor='w',text='LATEST',fill=MUTED,font=('Consolas',7,'bold'),tags='static')
        self.activity=self.bg.create_text(1310,188,anchor='nw',text='',fill=WHITE,font=('Consolas',8),width=245,tags='stream')
        self.bg.create_text(1310,640,anchor='w',text='F9  •  VOICE ON/OFF',fill=MUTED,font=('Consolas',7,'bold'),tags='static')
        caps=['OPEN ANYTHING','SEARCH ANYTHING','TYPE BY VOICE','MEDIA CONTROL','WINDOW CONTROL','SCREENSHOT','SYSTEM CONTROL','OLLAMA BRAIN']
        for i,c in enumerate(caps):
            x=45+i*190; self.bg.create_rectangle(x,775,x+165,813,fill=PANEL2,outline='#123447',tags='static'); self.bg.create_text(x+82,794,text=c,fill=CYAN if i<7 else PURPLE,font=('Consolas',7,'bold'),tags='static')
        self.status=self.bg.create_text(800,700,text='BOOTING',fill=CYAN,font=('Consolas',18,'bold'),tags='status')
        self.sub=self.bg.create_text(800,722,text='INITIALIZING NEURAL CHANNEL',fill=MUTED,font=('Consolas',8,'bold'),tags='status')
        self.entry=tk.Entry(self.root,bg='#071722',fg=WHITE,insertbackground=CYAN,relief='flat',font=('Segoe UI',12),highlightthickness=1,highlightbackground='#17465a',highlightcolor=CYAN)
        self.entry.place(relx=.235,rely=.91,relwidth=.42,height=43); self.entry.bind('<Return>',lambda e:self.submit()); self.entry.focus_set()
        self.button=tk.Button(self.root,text='EXECUTE  ◈',command=self.submit,bg='#0a2c42',fg=CYAN,activebackground='#124e6e',activeforeground=WHITE,relief='flat',font=('Consolas',9,'bold'))
        self.button.place(relx=.66,rely=.91,relwidth=.105,height=43)
    def set_status(self,state):
        self.mode=state
        def u():
            col={'LISTENING':ORANGE,'THINKING':PURPLE,'ERROR':RED,'READY':GREEN,'BOOTING':CYAN}.get(state,CYAN)
            self.bg.itemconfigure('status',text=state,fill=col); self.bg.itemconfigure(self.dot,fill=RED if state=='ERROR' else col)
        try:self.root.after(0,u)
        except:pass
    def add_log(self,who,msg):
        self.logs.append((who,msg)); self.logs=self.logs[-9:]
        def u():
            lines=[f'[{a}] {b}' for a,b in self.logs]; self.bg.itemconfigure('stream',text='\n'.join(lines))
        try:self.root.after(0,u)
        except:pass
    def submit(self):
        t=self.entry.get().strip(); self.entry.delete(0,'end')
        if t: threading.Thread(target=self.engine.handle,args=(t,),daemon=True).start()
    def toggle_voice(self):
        self.cfg['continuous_mode']=not self.cfg.get('continuous_mode',True); self.add_log('SYSTEM','Voice channel '+('enabled' if self.cfg['continuous_mode'] else 'disabled'))
    def start_voice(self):
        threading.Thread(target=self.voice_loop,daemon=True).start(); self.speaker.say('MAYA online. Final neural command center ready.'); self.set_status('READY')
    def voice_loop(self):
        while self.running and self.engine.running:
            if not self.cfg.get('continuous_mode',True): time.sleep(.2); continue
            t=self.listener.listen_once()
            if t: self.add_log('VOICE',t); self.engine.handle(t)
        self.running=False
    def animate(self):
        if not self.running:return
        self.frame+=1; self.wave+=.19; self.draw(); self.stats_update(); self.root.after(30,self.animate)
    def stats_update(self):
        vals=[]
        if psutil: vals=[f'{psutil.cpu_percent(None):04.1f}% CPU',f'{psutil.virtual_memory().percent:04.1f}% RAM']
        else: vals=['ACTIVE','ACTIVE']
        for i,v in enumerate(vals): self.bg.itemconfigure(self.stats[i+1],text=v,fill=CYAN)
        self.bg.itemconfigure(self.stats[0],text='LISTENING' if self.mode=='LISTENING' else 'READY',fill=ORANGE if self.mode=='LISTENING' else GREEN)
        self.bg.itemconfigure(self.stats[3],text='CONNECTED',fill=CYAN)
        self.bg.itemconfigure(self.stats[4],text='OLLAMA' if self.brain.enabled else 'RULES',fill=PURPLE if self.brain.enabled else MUTED)
    def draw(self):
        c=self.bg; c.delete('fx'); W=max(1,c.winfo_width()); H=max(1,c.winfo_height()); cx=W*.50; cy=405; p=self.frame
        # subtle grid / horizon
        for i in range(-12,13): c.create_line(cx,cy+120,cx+i*58,cy+330,fill=GRID,tags='fx')
        for j in range(9): c.create_arc(cx-330-j*30,cy+105+j*21,cx+330+j*30,cy+180+j*21,start=180,extent=180,style='arc',outline=GRID,tags='fx')
        # perspective circular rings
        for i in range(12):
            rx=90+i*18; ry=rx*.46; a=(p*(1.2+i*.08)+i*31)%360
            c.create_oval(cx-rx,cy-ry,cx+rx,cy+ry,outline='#0b3343',tags='fx')
            c.create_arc(cx-rx,cy-ry,cx+rx,cy+ry,start=a,extent=52,style='arc',outline=CYAN,width=2,tags='fx')
            c.create_arc(cx-rx,cy-ry,cx+rx,cy+ry,start=a+180,extent=24,style='arc',outline=BLUE,tags='fx')
        # vertical energy lattice
        for z in range(-4,5):
            yy=cy+z*34; rx=78-abs(z)*7
            c.create_arc(cx-rx,yy-rx*.22,cx+rx,yy+rx*.22,start=0,extent=180,style='arc',outline='#12627d',tags='fx')
        # orbiting nodes
        for i in range(18):
            a=p*.018+i*math.tau/18; rr=150+(i%3)*28; x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.48
            c.create_oval(x-3,y-3,x+3,y+3,fill=CYAN if i%3==0 else BLUE,outline='',tags='fx')
            c.create_line(cx+math.cos(a)*100,cy+math.sin(a)*100*.48,x,y,fill='#0e4056',tags='fx')
        # particle cloud deterministic
        random.seed(42)
        for i in range(170):
            a=i*.71+p*.006; rr=235+(i%19)*4; x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.47; r=1 if i%5 else 2
            c.create_oval(x-r,y-r,x+r,y+r,fill=CYAN if i%17==0 else '#164a60',outline='',tags='fx')
        # scan beam
        sy=cy-250+(p*3.6%500); c.create_line(cx-355,sy,cx+355,sy,fill='#0c6e8c',width=1,tags='fx')
        # core glow
        for i in range(24,0,-1):
            r=6+i*3; col='#%02x%02x%02x'%(8+i//2,65+i*4,88+i*5); c.create_oval(cx-r,cy-r,cx+r,cy+r,fill=col,outline='',tags='fx')
        c.create_oval(cx-39,cy-39,cx+39,cy+39,fill='#b9fbff',outline=CYAN,width=2,tags='fx'); c.create_oval(cx-14,cy-14,cx+14,cy+14,fill='white',outline='',tags='fx')
        c.create_text(cx,cy-285,text='◈ MAYA // NEURAL CORE',fill='#63b9cb',font=('Consolas',10,'bold'),tags='fx')
        # waveform
        base=cy+245
        for i in range(86):
            amp=4+28*abs(math.sin(self.wave+i*.39))*(.45+.55*abs(math.sin(i*.17+p*.018))); x=cx-340+i*8
            c.create_line(x,base-amp,x,base+amp,fill=CYAN if i%7==0 else '#17627c',width=2,tags='fx')
        c.create_text(cx,base+31,text='AUDIO CHANNEL  //  REAL-TIME EXECUTION',fill='#3e8497',font=('Consolas',8,'bold'),tags='fx')
    def close(self):
        self.running=False; self.engine.running=False
        try:self.root.destroy()
        except:pass
if __name__=='__main__': MayaApp().root.mainloop()
