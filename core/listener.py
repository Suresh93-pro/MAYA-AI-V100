import time
import numpy as np
import speech_recognition as sr
import sounddevice as sd

class Listener:
    def __init__(self,language='en-IN',timeout=3,phrase_time_limit=7,on_state=None):
        self.r=sr.Recognizer(); self.r.dynamic_energy_threshold=True
        self.language=language; self.timeout=float(timeout); self.limit=float(phrase_time_limit); self.on_state=on_state or (lambda s:None)
        self.rate=16000; self.chunk=.08
    def listen_once(self):
        try:
            self.on_state('LISTENING'); started=False; silence=0; chunks=[]; t0=time.time(); baseline=[]
            while time.time()-t0 < self.timeout+self.limit:
                n=int(self.rate*self.chunk); data=sd.rec(n,samplerate=self.rate,channels=1,dtype='int16'); sd.wait()
                a=data.reshape(-1).astype(np.float32); rms=float(np.sqrt(np.mean(a*a)))
                if not started:
                    baseline.append(rms); noise=float(np.median(baseline[-12:])); threshold=max(220,noise*2.35)
                    if rms>threshold: started=True; chunks.append(data.copy())
                else:
                    chunks.append(data.copy()); silence=0 if rms>330 else silence+self.chunk
                    if silence>=.62 and time.time()-t0>.55: break
                    if time.time()-t0>=self.limit: break
            if not chunks:self.on_state('READY'); return ''
            self.on_state('THINKING'); audio=np.concatenate(chunks,axis=0)
            text=self.r.recognize_google(sr.AudioData(audio.tobytes(),self.rate,2),language=self.language)
            self.on_state('READY'); return text.strip()
        except sr.UnknownValueError:self.on_state('READY'); return ''
        except sr.RequestError:self.on_state('ERROR'); return ''
        except Exception:self.on_state('ERROR'); return ''
