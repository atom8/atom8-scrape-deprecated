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


def get_settings():
    return etc.get_scraper_settings(etc.DEFAULT_SETTINGS_PATH)


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

    # Create an export directory
    try:
        etc.create_directory(timestamped_export_dir)
        print('Export directory created @ %s' %
              timestamped_export_dir)
    except OSError:
        return

    settings = get_settings()

    # Perform reddit scrape
    if settings['reddit']['enabled']:
        print('Performing Reddit scrape')
        reddit_control.scrape(
            settings['reddit']['subreddits'], timestamped_export_dir,
            verbose=True)

    # Perform tigsource scrape
    if settings['tigsource']['enabled']:
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

        app_settings = get_settings()

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
        self.reddit_enabled = app_settings['reddit']['enabled']
        self.reddit_status_label = tk.Label(
            reddit_frame,
            text='Enabled: %s' % self.reddit_enabled,
            bg='green' if self.reddit_enabled else 'red')
        self.reddit_status_label.pack()
        reddit_btns = tk.Frame(reddit_frame)
        reddit_btns.pack()
        open_reddit_settings_btn = tk.Button(reddit_btns, text='config')
        open_reddit_settings_btn.config(command=self.open_reddit_settings)
        open_reddit_settings_btn.grid(row=0, column=0)
        toggle_reddit_btn = tk.Button(reddit_btns, text='toggle')
        toggle_reddit_btn.config(command=self.toggle_reddit)
        toggle_reddit_btn.grid(row=0, column=1)

        # TIGsource
        TIG_frame = tk.Frame(right_frame)
        TIG_frame.pack()
        TIG_label = tk.Label(TIG_frame, text='TIGsource')
        TIG_label.pack()
        self.TIG_enabled = app_settings['tigsource']['enabled']
        self.TIG_status_label = tk.Label(
            TIG_frame,
            text='Enabled: %s' % self.TIG_enabled,
            bg='green' if self.TIG_enabled else 'red')
        self.TIG_status_label.pack()
        TIG_btns = tk.Frame(TIG_frame)
        TIG_btns.pack()
        open_TIG_settings_btn = tk.Button(TIG_btns, text='config')
        open_TIG_settings_btn.config(command=self.open_TIG_settings)
        open_TIG_settings_btn.grid(row=0, column=0)
        toggle_TIG_btn = tk.Button(TIG_btns, text='toggle')
        toggle_TIG_btn.config(command=self.toggle_TIG)
        toggle_TIG_btn.grid(row=0, column=1)

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
        # TODO backup settings
        # maximum of 100 subs

        app_settings = get_settings()

        settings = tk.Toplevel()
        settings.wm_title("Reddit settings")
        settings.geometry('320x240')

        tk.Label(settings, text="Subreddits").pack()

        # Add subreddit editting frame
        subs_frame = tk.Frame(settings)
        subs_frame.pack()

        # get data from app settings
        sub_data = app_settings['reddit']['subreddits']

        # A list containing references to each entry. Each entry is a tuple.
        sub_entries = []

        sr = 0
        for sub in sub_data:
            name = tk.Entry(subs_frame)
            name.insert(0, sub['name'])
            name.grid(row=sr, column=0)

            min_karma = tk.Entry(subs_frame)
            min_karma.insert(0, sub['min_karma'])
            min_karma.grid(row=sr, column=1)

            sub_entries.append((name, min_karma))
            sr += 1

        # functionality for Add button
        def add_subreddit():
            nonlocal sub_entries

            # row index to insert into
            row = len(sub_entries)

            # name doesnt matter because theres nothing in there.
            a = tk.Entry(subs_frame)
            b = tk.Entry(subs_frame)
            a.grid(row=row, column=0)
            b.grid(row=row, column=1)
            sub_entries.append((a, b))

        # functionality for Delete button
        def delete_subreddit():
            pass

        # Add manip buttons TO subreddit edit frame
        edit_buttons = tk.Frame(settings)
        edit_buttons.pack()
        add_btn = tk.Button(edit_buttons, text='Add', command=add_subreddit)
        add_btn.grid(row=100, column=0)
        # delete_btn = tk.Button(edit_buttons, text='Delete')
        # delete_btn.grid(row=100, column=1)

        # Apply Button functionality
        def apply_settings():
            '''save settings to settings.json'''
            nonlocal app_settings

            # TODO validate

            subs = []
            for se_name, se_karma in sub_entries:
                if se_name.get().strip():
                    subs.append(
                        {'name': se_name.get(), 'min_karma': int(se_karma.get())}
                    )

            app_settings['reddit']['subreddits'] = subs
            etc.export_settings(etc.DEFAULT_SETTINGS_PATH, app_settings)

            settings.destroy()

        # Add edit buttons
        exit_buttons = tk.Frame(settings)
        exit_buttons.pack(side='bottom')
        apply_btn = tk.Button(exit_buttons, text="Apply",
                              command=apply_settings)
        apply_btn.grid(row=0, column=0)
        cancel_btn = tk.Button(exit_buttons, text='Cancel',
                               command=settings.destroy)
        cancel_btn.grid(row=0, column=1)

    def open_TIG_settings(self):

        app_settings = get_settings()

        diag = tk.Toplevel()
        diag.wm_title("TIG settings")

        tk.Label(diag, text="Topics").pack()

        # Add topic editting frame
        topics_frame = tk.Frame(diag)
        topics_frame.pack()

        # get "topics" from app settings
        topics_data = app_settings['tigsource']['topics']

        # A list containing references to each entry.
        topic_entries = []
        row_x = 0
        for topic_no in topics_data:
            topic_entry = tk.Entry(topics_frame)
            topic_entry.insert(0, topic_no)
            topic_entry.grid(row=row_x, column=0)
            topic_entries.append(topic_entry)
            row_x += 1

        # add topic
        def add_topic():
            nonlocal topic_entries

            # row index to insert into
            row = len(topic_entries)

            pending = tk.Entry(topics_frame)
            pending.grid(row=row, column=0)
            topic_entries.append(pending)

        # remove topic
        def remove_topic():
            pass

        # Manip buttons
        edit_buttons = tk.Frame(diag)
        edit_buttons.pack()
        add_btn = tk.Button(edit_buttons, text='Add', command=add_topic)
        add_btn.grid(row=100, column=0)

        # Apply settings
        def apply_settings():
            nonlocal app_settings

            topics = []
            for topic_entry in topic_entries:
                if topic_entry.get().strip():
                    topics.append(int(topic_entry.get()))

            app_settings['tigsource']['topics'] = topics
            etc.export_settings(etc.DEFAULT_SETTINGS_PATH, app_settings)

            diag.destroy()

        # Add final buttons
        exit_buttons = tk.Frame(diag)
        exit_buttons.pack(side='bottom')
        apply_btn = tk.Button(exit_buttons, text="Apply",
                              command=diag.destroy)
        apply_btn.grid(row=0, column=0)
        cancel_btn = tk.Button(exit_buttons, text='Cancel',
                               command=diag.destroy)
        cancel_btn.grid(row=0, column=1)

    def toggle_reddit(self):
        self.reddit_enabled = not self.reddit_enabled
        if self.reddit_enabled:
            status = 'Enabled: True'
            color = 'green'
        else:
            status = 'Enabled: False'
            color = 'red'
        self.reddit_status_label.config(text=status, bg=color)

        app_settings = get_settings()
        app_settings['reddit']['enabled'] = self.reddit_enabled
        etc.export_settings(etc.DEFAULT_SETTINGS_PATH, app_settings)

    def toggle_TIG(self):
        self.TIG_enabled = not self.TIG_enabled
        if self.TIG_enabled:
            status = 'Enabled: True'
            color = 'green'
        else:
            status = 'Enabled: False'
            color = 'red'
        self.TIG_status_label.config(text=status, bg=color)

        app_settings = get_settings()
        app_settings['tigsource']['enabled'] = self.TIG_enabled
        etc.export_settings(etc.DEFAULT_SETTINGS_PATH, app_settings)

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
