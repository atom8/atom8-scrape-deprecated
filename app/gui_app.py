import sys
import time
import threading

import tkinter as tk
from tkinter import filedialog

from . import etc
from . import reddit as reddit_control
from . import tigsource as tigsource_control

APP_WIDTH = 960
APP_HEIGHT = 640

EXPORT_DIRECTORY = None
REQUEST_SCRAPE = False


class ScrapeThreadWrapper():
    def __init__(self):
        self.scraper_thread = threading.Thread(target=self.run, args=())
        self.scraper_thread.daemon = True
        self.scraper_thread.start()

    def run(self):
        global REQUEST_SCRAPE

        while True:
            if REQUEST_SCRAPE:
                REQUEST_SCRAPE = False
                print('*** SCRAPE STARTED ***')
                result = perform_scrape(EXPORT_DIRECTORY)
                if result == 0:
                    print('*** SCRAPE COMPLETED ***')
                else:
                    print('*** SCRAPE STOPPED ***')
            time.sleep(1)


def perform_scrape(export_directory):
    if export_directory is None:
        print('[ERROR] ~ specify an export directory')
        return

    timestamped_export_dir = etc.timestamp_directory(export_directory)

    # Create export directory
    try:
        etc.create_directory(timestamped_export_dir)
        print('Export directory created @ %s' %
              timestamped_export_dir)
    except OSError:
        return

    settings = etc.get_scraper_settings('settings.json')

    # TODO if reddit enable
    print('Performing Reddit scrape')
    reddit_control.scrape(
        settings['reddit']['subreddits'], timestamped_export_dir,
        verbose=True)

    # TODO if TIG enable
    print('Performing TIGsource scrape')
    tigsource_control.scrape(
        settings['tigsource']['topics'], timestamped_export_dir,
        verbose=True)

    return 0


class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs),
        self.parent = parent

        self.export_directory = None

        # Left division
        left_frame = tk.Frame(self)
        left_frame.pack(side='left', padx=10, pady=10, 
                        fill=tk.BOTH, expand=True)

        # Export destinaction
        export_frame = tk.Frame(left_frame)
        export_frame.pack()
        self.export_label = tk.Label(export_frame, text='Export to: ')
        self.export_label.pack(side='left', padx=10)
        tk.Button(export_frame, text='Browse',
                  command=self.do_change_destination_folder).pack(side='right')

        # Output diag
        output_frame = tk.Frame(left_frame)
        output_frame.pack(side='bottom', padx=10, pady=10,
                          fill=tk.BOTH, expand=True)

        tk.Label(output_frame, text='Output').pack(fill=tk.X)
        self.output = tk.Text(output_frame, height=10, width=40)
        self.output.insert(tk.END, 'Welcome to GDI scrape\n')
        self.output.pack(side='left', fill=tk.BOTH, expand=True)
        out_scroll = tk.Scrollbar(output_frame)
        out_scroll.config(command=self.output.yview)
        self.output.config(yscrollcommand=out_scroll.set)
        out_scroll.pack(side='right', fill=tk.Y)

        # Right division
        right_frame = tk.Frame(self, borderwidth=2, relief="groove")
        right_frame.pack(side='right', fill='both', padx=10, pady=10)

        # Reddit
        reddit_frame = tk.Frame(right_frame)
        reddit_frame.pack()
        reddit_label = tk.Label(reddit_frame, text='Reddit')
        reddit_label.pack()
        self.reddit_status_label = tk.Label(reddit_frame, text='Status: disabled')
        self.reddit_status_label.pack()
        open_reddit_settings_btn = tk.Button(reddit_frame, text='config')
        open_reddit_settings_btn.config(command=self.open_reddit_settings)
        open_reddit_settings_btn.pack()

        # TIGsource
        TIG_frame = tk.Frame(right_frame)
        TIG_frame.pack()
        TIG_label = tk.Label(TIG_frame, text='TIGsource')
        TIG_label.pack()
        self.TIG_status_label = tk.Label(TIG_frame, text='Status: disabled')
        self.TIG_status_label.pack()
        open_TIG_settings_btn = tk.Button(TIG_frame, text='config')
        open_TIG_settings_btn.config(command=self.open_TIG_settings)
        open_TIG_settings_btn.pack()

        # Perform scape
        perform_btn = tk.Button(right_frame, text='PERFORM SCRAPE')
        perform_btn.config(command=self.request_scrape)
        perform_btn.pack(side='bottom', padx=10, pady=10)

        # Set sysout to output_textbox
        sys.stdout = StdoutRedirector(self.output)

    def do_change_destination_folder(self):
        destination_folder = filedialog.askdirectory()

        self.export_directory = destination_folder

        self.export_label.config(text='Export to: ' + destination_folder)
        self.print_message('Export folder changed ~ %s' % destination_folder)

    def request_scrape(self):
        global EXPORT_DIRECTORY
        global REQUEST_SCRAPE

        EXPORT_DIRECTORY = self.export_directory
        REQUEST_SCRAPE = True

        self.print_message("scrape requested")

    def open_reddit_settings(self):
        win = tk.Toplevel()
        win.wm_title("Reddit settings")

        tk.Label(win, text="Subreddits").grid(row=0, column=0)

        b = tk.Button(win, text="Okay", command=win.destroy)
        b.grid(row=1, column=0)

    def open_TIG_settings(self):
        win = tk.Toplevel()
        win.wm_title("Reddit settings")

        tk.Label(win, text="Topics").grid(row=0, column=0)

        b = tk.Button(win, text="Okay", command=win.destroy)
        b.grid(row=1, column=0)

    def print_message(self, message):
        self.output.insert(tk.END, message + '\n')
        self.output.update()


class StdoutRedirector(object):
    '''Redirect all print statements to a textarea. Used by MainApplication.'''
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert(tk.END, string)
        self.text_space.update()


def run_app():
    root = tk.Tk()
    root.title('GDI Scraper')
    root.geometry('%sx%s' % (APP_WIDTH, APP_HEIGHT))

    # Change back stdout from MainApplication output before exiting program
    def on_closing():
        sys.stdout = sys.__stdout__
        root.destroy()
    root.protocol('WM_DELETE_WINDOW', on_closing)

    # Create main application frame. Remainder of view logic is inside here.
    MainApplication(root).pack(side="top", fill="both", expand=True)

    # scraper thread is started automatically through wrapper.
    ScrapeThreadWrapper()

    root.mainloop()
