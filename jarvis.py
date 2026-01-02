import tkinter as tk
import threading
import subprocess
import time
import math
import urllib.request
import urllib.parse
import shutil
import os
import json
import random
import struct
from datetime import datetime

# --- CONFIGURATION ---
USER_NAME = "Brathap"
AI_NAME = "J.A.R.V.I.S."

# ⚠️ UPDATE CONTACTS (Format: CountryCode+Number, No +)
#CONTACTS = {
#}

# --- UNIVERSAL COMMAND MAP ---
AUTOMATION_MAP = {
    "play": ("https://www.youtube.com/results?search_query=", ""),
    "search": ("https://www.google.com/search?q=", ""),
    "google": ("https://www.google.com/search?q=", ""),
    "github": ("https://github.com/search?q=", "")
}

WEBSITES = {
    "whatsapp": "https://web.whatsapp.com",
    "skillrack": "https://www.skillrack.com"
}

COLOR_ACCENT = "#00ffff"
COLOR_DIM = "#004444"
COLOR_BG = "#000000"

class JarvisRectified:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{AI_NAME} | SYSTEM RECTIFIED")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLOR_BG)
        
        # Center Window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - 550
        y = (screen_height // 2) - 350
        self.root.geometry(f"1100x700+{x}+{y}")

        # --- VISUALS ---
        self.left_frame = tk.Frame(root, bg=COLOR_BG, width=550, height=700)
        self.left_frame.pack(side="left", fill="y")
        self.canvas = tk.Canvas(self.left_frame, bg=COLOR_BG, width=550, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.right_frame = tk.Frame(root, bg=COLOR_BG, width=550, height=700)
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        # Input
        self.input_frame = tk.Frame(self.right_frame, bg=COLOR_BG)
        self.input_frame.pack(side="bottom", fill="x", padx=30, pady=40)
        
        self.entry = tk.Entry(self.input_frame, bg="#050505", fg=COLOR_ACCENT, insertbackground=COLOR_ACCENT, font=("Consolas", 13), bd=1, relief="solid")
        self.entry.bind("<Return>", self.handle_text)
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        
        # Controls
        btn_mic = tk.Button(self.input_frame, text="[ TALK ]", bg="#002222", fg=COLOR_ACCENT, command=self.trigger_mic, relief="flat", font=("Consolas", 9, "bold"))
        btn_mic.pack(side="right", ipadx=10, ipady=4, padx=2)
        btn_stop = tk.Button(self.input_frame, text="[ STOP ]", bg="#330000", fg="#ff5555", command=self.stop_all, relief="flat", font=("Consolas", 9, "bold"))
        btn_stop.pack(side="right", ipadx=10, ipady=4, padx=2)
        btn_wipe = tk.Button(self.input_frame, text="[ WIPE ]", bg="#332200", fg="#ffff55", command=self.clear_memory_action, relief="flat", font=("Consolas", 9, "bold"))
        btn_wipe.pack(side="right", ipadx=10, ipady=4, padx=2)

        # Header
        self.header = tk.Label(self.right_frame, text="/// STATUS: OPERATIONAL ///", bg=COLOR_BG, fg=COLOR_DIM, font=("Consolas", 10))
        self.header.pack(side="top", anchor="w", padx=30, pady=20)
        
        # Log
        self.chat_log = tk.Text(self.right_frame, bg="#020202", fg="#bbbbbb", font=("Consolas", 11), 
                                bd=0, padx=25, pady=25, wrap="word", state="disabled")
        self.chat_log.pack(side="top", fill="both", expand=True)
        
        self.chat_log.tag_config("AI", foreground=COLOR_ACCENT, font=("Consolas", 11, "bold"))
        self.chat_log.tag_config("YOU", foreground="#ffffff")
        self.chat_log.tag_config("SYS", foreground="#00ff00", font=("Consolas", 9))
        self.chat_log.tag_config("ERR", foreground="#ff3333", font=("Consolas", 9))

        # --- STATE ---
        self.history_file = "jarvis_memory.json"
        self.history = self.load_memory()
        self.player = self.find_audio_player()
        self.cx, self.cy = 275, 350
        self.tick = 0
        self.audio_level = 0
        self.mic_active = True
        self.processing = False
        self.stop_signal = False
        self.current_proc = None 

        if shutil.which("wtype"): self.typer_tool = "wtype"
        elif shutil.which("xdotool"): self.typer_tool = "xdotool"
        else: self.typer_tool = None

        threading.Thread(target=self.monitor_audio, daemon=True).start()
        self.animate_hud()
        self.speak(f"System rectified. Ready.")

    # --- CORE ---
    def load_memory(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_memory(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-50:], f, indent=4)
        except:
            pass
    
    def clear_memory_action(self):
        self.history = []
        self.save_memory()
        self.instant_log("SYS", "Memory Wiped.")
        self.speak("Memory erased.")

    def stop_all(self):
        self.stop_signal = True
        self.processing = False
        self.instant_log("SYS", "Action Stopped.")
        if self.current_proc:
            try: self.current_proc.terminate()
            except: pass

    def find_audio_player(self):
        for p in ["mpv", "ffplay", "paplay", "spd-say"]:
            if shutil.which(p): return p
        return None

    def instant_log(self, sender, message):
        self.chat_log.config(state="normal")
        self.chat_log.insert(tk.END, f"\n[{sender}]: {message}")
        self.chat_log.see(tk.END)
        self.chat_log.config(state="disabled")

    def speak(self, text):
        if not self.player: return
        self.stop_signal = False
        def run():
            chunks = text.replace("?", "?|").replace(".", ".|").replace("!", "!|").split("|")
            for chunk in chunks:
                if self.stop_signal: break
                if not chunk.strip(): continue
                try:
                    if self.player == "spd-say":
                        self.current_proc = subprocess.Popen(["spd-say", "-r", "-10", chunk])
                        self.current_proc.wait()
                    else:
                        try:
                            q = urllib.parse.quote(chunk)
                            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
                            fn = "/tmp/voice.mp3"
                            urllib.request.urlretrieve(url, fn)
                            self.current_proc = subprocess.Popen([self.player, fn], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            self.current_proc.wait()
                        except: pass
                except: pass
        threading.Thread(target=run).start()

    def monitor_audio(self):
        try:
            process = subprocess.Popen(["arecord", "-f", "S16_LE", "-r", "8000", "-c", "1", "-t", "raw"],
                                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            while self.mic_active:
                raw = process.stdout.read(512)
                if not raw: break
                shorts = struct.unpack(f"{len(raw)//2}h", raw)
                vol = sum(abs(s) for s in shorts) / len(shorts)
                target = vol / 50
                self.audio_level = (self.audio_level * 0.8) + (target * 0.2)
        except: self.audio_level = 0.5

    def animate_hud(self):
        self.canvas.delete("all")
        self.tick += 1
        
        if self.processing:
            spin_speed = 20
            status = "PROCESSING..."
            core_color = "#ffffff"
        else:
            spin_speed = 2 + (self.audio_level * 10)
            status = "SYSTEM ONLINE"
            core_color = COLOR_ACCENT

        rotation = (self.tick * spin_speed) % 360
        pulse = math.sin(self.tick * 0.1) * 10 + (self.audio_level * 15)
        
        self.canvas.create_oval(self.cx-50-pulse, self.cy-50-pulse, self.cx+50+pulse, self.cy+50+pulse, outline=COLOR_DIM, width=2)
        self.canvas.create_oval(self.cx-20-(pulse*0.5), self.cy-20-(pulse*0.5), self.cx+20+(pulse*0.5), self.cy+20+(pulse*0.5), fill=core_color, outline="")

        r_inner = 90
        for i in range(3):
            start = rotation + (i * 120)
            self.canvas.create_arc(self.cx-r_inner, self.cy-r_inner, self.cx+r_inner, self.cy+r_inner,
                                   start=start, extent=80, outline=COLOR_ACCENT, width=4, style="arc")

        r_outer = 130
        for i in range(0, 360, 10):
            rad = math.radians(i - rotation)
            x1 = self.cx + math.cos(rad) * r_outer
            y1 = self.cy + math.sin(rad) * r_outer
            x2 = self.cx + math.cos(rad) * (r_outer + 15)
            y2 = self.cy + math.sin(rad) * (r_outer + 15)
            color = COLOR_ACCENT if i % 40 == 0 else COLOR_DIM
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
            
        self.canvas.create_text(self.cx, 600, text=status, fill=COLOR_ACCENT, font=("Consolas", 12, "bold"))
        self.root.after(30, self.animate_hud)

    # --- BRAIN ---
    def trigger_mic(self):
        self.stop_signal = False
        threading.Thread(target=self.listen_logic).start()

    def listen_logic(self):
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.processing = False
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio = r.listen(source, timeout=4, phrase_time_limit=4)
            self.instant_log("SYS", "Hearing...")
            cmd = r.recognize_google(audio).lower()
            self.handle_command(cmd)
        except:
            self.instant_log("ERR", "Voice unclear.")

    def handle_text(self, event):
        cmd = self.entry.get()
        self.entry.delete(0, tk.END)
        self.handle_command(cmd)

    def handle_command(self, cmd):
        cmd = cmd.lower().strip()
        self.instant_log("YOU", cmd)
        self.stop_signal = False
        
        # 1. WHATSAPP AUTOMATION
        if "send" in cmd and "message" in cmd and "to" in cmd:
            try:
                parts = cmd.split("to ", 1)[1] 
                target_name = parts.split(" ")[0] 
                if "that " in parts: message = parts.split("that ", 1)[1]
                else: message = parts.replace(target_name, "", 1).strip()
                
                target_number = CONTACTS.get(target_name)
                
                if target_number:
                    self.instant_log("SYS", f"Target: {target_name} | Msg: {message}")
                    self.speak(f"Sending to {target_name}.")
                    
                    # USE URL TEXT PRE-FILL (Reliable)
                    url = f"https://web.whatsapp.com/send?phone={target_number}&text={urllib.parse.quote(message)}"
                    self.execute_browser_automation(url, mode="whatsapp")
                else:
                    self.instant_log("ERR", "Contact not found.")
            except: self.instant_log("ERR", "Command error.")
            return

        # 2. UNIVERSAL WEB AUTOMATION
        first_word = cmd.split(" ")[0]
        if first_word in AUTOMATION_MAP:
            query = cmd.replace(first_word, "", 1).strip()
            prefix, suffix = AUTOMATION_MAP[first_word]
            full_url = f"{prefix}{urllib.parse.quote(query)}{suffix}"
            
            self.instant_log("SYS", f"Executing: {first_word} '{query}'")
            self.speak(f"Executing {first_word}.")
            self.execute_browser_automation(full_url, mode="open")
            return

        # 3. GENERIC TYPING
        if cmd.startswith("type ") or cmd.startswith("write "):
            text = cmd.replace("type ", "", 1).replace("write ", "", 1)
            self.instant_log("SYS", f"Typing in 4s: '{text}'")
            self.speak("Typing in four seconds.")
            self.root.after(4000, lambda: self.execute_keys(text))
            return

        # 4. APP LAUNCHER
        if "open" in cmd:
            target = cmd.replace("open", "").strip()
            if target in WEBSITES:
                subprocess.Popen(["firefox", WEBSITES[target]])
                self.speak(f"Opening {target}")
            else:
                subprocess.Popen(f"nohup {target} >/dev/null 2>&1 &", shell=True)
                self.speak(f"Launching {target}")
            return

        # 5. AI CHAT
        self.processing = True
        threading.Thread(target=self.ask_multibrain, args=(cmd,)).start()

    def execute_browser_automation(self, url, mode="open"):
        subprocess.Popen(["firefox", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if mode == "whatsapp" and self.typer_tool:
            def sequence():
                # 20 second countdown for loading
                for i in range(20, 0, -1):
                    if i <= 5: self.instant_log("SYS", f"Load: {i}...")
                    time.sleep(1)
                
                self.instant_log("SYS", "Waking up chat...")
                
                # THE WAKE UP TRICK: SPACE -> BACKSPACE -> ENTER
                # This activates the grayed out send button
                if self.typer_tool == "wtype":
                    subprocess.run(["wtype", " "]) 
                    time.sleep(0.2)
                    subprocess.run(["wtype", "-k", "BackSpace"])
                    time.sleep(0.5)
                    subprocess.run(["wtype", "-k", "Return"])
                elif self.typer_tool == "xdotool":
                    subprocess.run(["xdotool", "key", "space"])
                    time.sleep(0.2)
                    subprocess.run(["xdotool", "key", "BackSpace"])
                    time.sleep(0.5)
                    subprocess.run(["xdotool", "key", "Return"])

                self.instant_log("SYS", "SENT.")
                
            threading.Thread(target=sequence).start()

    def execute_keys(self, text, enter=False):
        if not self.typer_tool:
            self.instant_log("ERR", "Install 'wtype'!")
            return
        try:
            if self.typer_tool == "wtype":
                if text: subprocess.run(["wtype", "-d", "50", text])
                if enter: subprocess.run(["wtype", "-k", "Return"])
            elif self.typer_tool == "xdotool":
                if text: subprocess.run(["xdotool", "type", "--delay", "50", text])
                if enter: subprocess.run(["xdotool", "key", "Return"])
        except: pass

    def ask_multibrain(self, prompt):
        if self.stop_signal: return
        context = ""
        for entry in self.history[-3:]: context += f"U: {entry['user']} | A: {entry['ai']}\n"
        sys_msg = f"You are {AI_NAME}. User is {USER_NAME}. Memory:\n{context}\nAnswer: {prompt}"
        safe_q = urllib.parse.quote(sys_msg)
        seed = random.randint(100, 99999)

        urls = [
            f"https://text.pollinations.ai/{safe_q}?model=openai&seed={seed}",
            f"https://text.pollinations.ai/{safe_q}?model=mistral&seed={seed}",
            f"https://text.pollinations.ai/{safe_q}?model=unity&seed={seed}"
        ]

        for url in urls:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=20) as res:
                    if self.stop_signal: return
                    raw = res.read().decode('utf-8')
                    self.process_response(prompt, raw)
                    return 
            except: continue

        self.processing = False
        self.instant_log("ERR", "Servers busy.")
        self.speak("I cannot reach the servers.")

    def process_response(self, prompt, raw_response):
        if self.stop_signal: return
        response = raw_response.replace("AI:", "").strip().replace("*", "").replace("#", "")
        self.processing = False
        self.instant_log("AI", response)
        self.speak(response)
        self.history.append({"user": prompt, "ai": response})
        self.save_memory()

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisRectified(root)
    root.mainloop()
