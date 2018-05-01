import tkinter as tk
import random
import sounddevice as sd
import queue
import numpy as np

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Fancy indexing with mapping creates a (necessary!) copy:
    q.put(indata[::10, :2])


class ChangeTime:
    def __init__(self, root=None):
        self.root = root
        h_screen_width = root.winfo_screenwidth()//2
        
        #Make left window
        root.overrideredirect(True) # disable your window to be closed by regular.
        root.wm_attributes("-alpha", 0.7) # alpha
        root.wm_attributes("-topmost", 1) # always place on top
        #root.wm_attributes("-toolwindow", True) # only x button in title bar
        root.geometry("+"+str(h_screen_width-110)+"+0") # location of window
        self.w_left = tk.Canvas(root, width=100, height=150)
        self.r_left = self.w_left.create_rectangle(0, 0, 100, 150, fill="blue")
        self.w_left.pack()  

        #Make right window
        right = tk.Toplevel(root)
        right.overrideredirect(True)
        right.wm_attributes("-alpha", 0.7)
        right.wm_attributes("-topmost", 1)
        right.wm_attributes("-toolwindow", True)
        right.geometry("+"+str(h_screen_width+10)+"+0")
        self.w_right = tk.Canvas(right, width=100, height=150)
        self.r_right = self.w_right.create_rectangle(0, 0, 100, 150, fill="blue")
        self.w_right.pack()

        #Call self.newtime after 1000ms
        self.listenID = self.root.after(100, self.update_plot) 
        #self.update_plot()

    def update_plot(self):
        updated = False
        while True:
            try:
                data = q.get_nowait()
            except queue.Empty:
                #print ("Queue Empty")
                break
            if updated: # Update only once.
                continue
            updated = True
            left_sound = np.mean(np.absolute(data[:,0]),0)
            right_sound = np.mean(np.absolute(data[:,1]),0)
            if left_sound > right_sound: # Weight difference.
                left_sound = left_sound*5
                right_sound = right_sound/5
            else:
                right_sound = right_sound*5
                left_sound = left_sound/5
            #print ("d:",[left_sound,right_sound] )
            #print ("c:",[20-int(20.*left_sound), 0, 20+int(20.*left_sound), int(100.*left_sound)])
            self.w_left.coords(self.r_left, 50-int(50.*left_sound), 75-int(75*left_sound), 50+int(50*left_sound), 75+int(75*left_sound))
            self.w_right.coords(self.r_right, 50-int(50.*right_sound), 75-int(75*right_sound), 50+int(50*right_sound), 75+int(75*right_sound))
            
        self.listenID = self.root.after(100, self.update_plot)
        

def main(): 
    device_info = sd.query_devices(None, 'input')
    samplerate = device_info['default_samplerate']
    try:
        stream = sd.InputStream(
            device=None, channels=2,
            samplerate= samplerate, callback=audio_callback)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))

    root = tk.Tk()
    ChangeTime(root)
    with stream:
        root.mainloop()

if __name__ == '__main__':
    main()
