# monitor.py
import threading
import time
import tkinter as tk
import socketio
import os
import builtins
import listeners
from display import TaskDisplay
import display
import calibrate
import rewind
import controller
# Redefine print function
listener = None
oldprint = builtins.print

def custom_print(*args, **kwargs):
    oldprint("mon:", *args, **kwargs, flush=True)

# Replace built-in print with custom print
builtins.print = custom_print



# ... (keep the existing imports and print redefinition)

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.calibrate_dialog_flag = False
        self.sio = socketio.Client()
        self.setup_sockets()

    def setup_sockets(self):
        PORT = os.environ.get('PORT', 3000)

        @self.sio.event
        def connect():
            print('Connected to server')
            self.sio.emit('session?', 'monitor')

        @self.sio.on('session:')
        def session(session_id):
            print("Session created", session_id)

        @self.sio.event
        def disconnect():
            print('Disconnected from server')

        @self.sio.on('calibrate')
        def on_calibrate(data):
            print('Received calibrate message:', data)
            self.calibrate_dialog_flag = True

        @self.sio.on('rewind')
        def on_rewind(data):
            print('Received Rewind message:', data)
            controller.test()
        # Connect to the server
        timeout = 1
        while True:
            try:
                self.sio.connect(f'http://localhost:{PORT}')
                break
            except Exception as e:
                if timeout != 1:
                    print(f"Connection failed: {e}. Retrying in {timeout} seconds...")
                time.sleep(timeout)
                timeout += 1

    def check_calibrate(self):
        if self.calibrate_dialog_flag:
            self.show_calibrate_dialog()
        self.root.after(1000, self.check_calibrate)  # Check every second

    def show_calibrate_dialog(self):
        self.calibrate_dialog_flag = False
        cal = calibrate.Calibrate(self.root)
        cal.create_dialog()

    def run(self):
        self.check_calibrate()
        self.root.mainloop()

def heartbeat():
    minutes = 0
    while True:
        time.sleep(60)
        minutes += 1
        print(f"Monitor up for {minutes} minutes")

def main():
    heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()

    app = Application()
    # controller.test()

    app.run()
if __name__ == "__main__":
    main()