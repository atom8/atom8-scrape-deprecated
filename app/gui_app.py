import enum
import os
import sys
import time
import threading

from datetime import datetime

import tkinter as tk
from tkinter import filedialog

from . import etc
from . import reddit as reddit_control
from . import tigsource as tigsource_control
from . import tumblr as tumblr_control
from . import twitter as twitter_control

APP_WIDTH = 960
APP_HEIGHT = 640

# Scrape thread will perform a scrape when this flag is set to true
REQUEST_SCRAPE = False

# Directory the scrape exports images and data to
EXPORT_DIRECTORY = None

# Amount of days to scrape
SCRAPE_RANGE = 0

# configuration file
CONFIG = None

# JSON file containing current settings
CURRENT_SETTINGS = None


class ScrapeRange(enum.IntEnum):
    '''An enum that specifies the different range options for scraper.'''
    CUSTOM = 1,
    SINCE_LAST = 2,
    ONE_WEEK = 3


def change_settings(settings_filename):
    global CURRENT_SETTINGS
    try:
        settings_file = etc.retrieve_JSON(settings_filename)
    except FileNotFoundError:
        print("ERROR: Settings file \"%s\" not found" % settings_filename)
        return None

    CURRENT_SETTINGS = settings_file

    return CURRENT_SETTINGS


def get_settings():
    return CURRENT_SETTINGS


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
                print('*** SCRAPE STARTING ***')
                print('Scrape Range: %d days' % SCRAPE_RANGE)
                result = perform_scrape(EXPORT_DIRECTORY, SCRAPE_RANGE)
                if result == 0:
                    print('*** SCRAPE COMPLETED ***')
                else:
                    print('*** SCRAPE STOPPED ***')
            time.sleep(1)


def perform_scrape(export_directory, days):
    if export_directory is None or not export_directory:
        print('[ERROR] ~ specify an export directory')
        return

    if not os.path.isdir(export_directory):
        print('[ERROR] ~ the export directory (%s) does not exist' %
              export_directory)
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
            verbose=True, days=days)

    # Perform tigsource scrape
    if settings['tigsource']['enabled']:
        print('Performing TIGsource scrape')
        tigsource_control.scrape(
            settings['tigsource']['topics'], timestamped_export_dir,
            verbose=True, days=days)

    # Perform tumblr scrape
    if settings['tumblr']['enabled']:
        print('Performing tumblr scrape')
        tumblr_control.scrape(
            settings['tumblr']['blogs'], timestamped_export_dir,
            verbose=True, days=days)

    # Perform twitter scrape
    if settings['twitter']['enabled']:
        print('Performing Twitter scrape')
        twitter_control.scrape(
            settings['twitter']['users'], timestamped_export_dir,
            verbose=True, days=days)

    settings['all']['last_scrape_date'] = str(datetime.now().date())
    etc.export_settings(etc.DEFAULT_SETTINGS_PATH, settings)

    return 0


class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs),
        self.parent = parent

        app_settings = get_settings()

        self.export_directory = app_settings['all']['export_directory']

        # Left division
        left_frame = tk.Frame(self)
        left_frame.pack(side='left', padx=10, pady=10,
                        fill=tk.BOTH, expand=True)

        # Export destinaction
        export_frame = tk.Frame(left_frame)
        export_frame.pack()
        self.export_label = tk.Label(
            export_frame,
            text='Export to: %s' % self.export_directory)
        self.export_label.pack(side='left', padx=10)
        tk.Button(export_frame, text='Browse',
                  command=self.do_change_destination_folder).pack(side='right')

        # Scrape range
        scrape_range_frame = tk.Frame(left_frame)
        scrape_range_frame.pack()
        scrape_ranges = [
            ('Since Last', ScrapeRange.SINCE_LAST.value),
            ('7 Days', ScrapeRange.ONE_WEEK.value),
            # ScrapeRange.CUSTOM is added later because it needs more logic.
        ]
        self.scrape_range_var = tk.IntVar()
        self.scrape_range_var.set(ScrapeRange.SINCE_LAST.value)
        tk.Label(scrape_range_frame, text='Scrape Range').pack(anchor=tk.W)
        for text, val in scrape_ranges:
            tk.Radiobutton(
                scrape_range_frame, text=text, variable=self.scrape_range_var,
                value=val
            ).pack(anchor=tk.W)
        # Custom scrape entry field
        # Made using a grid so that the Entry and the Radiobutton are adjacent.
        scrape_range_custom_frame = tk.Frame(scrape_range_frame)
        tk.Radiobutton(
            scrape_range_custom_frame, text='Custom',
            variable=self.scrape_range_var, value=ScrapeRange.CUSTOM.value
        ).grid(row=0, column=0)
        self.scrape_range_custom_entry = tk.Entry(scrape_range_custom_frame)
        self.scrape_range_custom_entry.grid(row=0, column=1)
        scrape_range_custom_frame.pack()
        # Last scrape on
        # read last scrape on from settings and put it into a label.
        last_scrape_on = app_settings['all'].get('last_scrape_date')
        self.last_scrape_on_label = tk.Label(
            scrape_range_frame,
            text='Last successful scrape: %s' % last_scrape_on)
        self.last_scrape_on_label.pack()

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
        reddit_frame.pack(pady=5)
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
        TIG_frame.pack(pady=5)
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

        # tumblr
        tumblr_frame = tk.Frame(right_frame)
        tumblr_frame.pack(pady=5)
        tumblr_label = tk.Label(tumblr_frame, text='tumblr')
        tumblr_label.pack()
        self.tumblr_enabled = app_settings['tumblr']['enabled']
        self.tumblr_status_label = tk.Label(
            tumblr_frame,
            text='Enabled: %s' % self.tumblr_enabled,
            bg='green' if self.tumblr_enabled else 'red')
        self.tumblr_status_label.pack()
        tumblr_btns = tk.Frame(tumblr_frame)
        tumblr_btns.pack()
        open_tumblr_settings_btn = tk.Button(tumblr_btns, text='config')
        open_tumblr_settings_btn.config(command=self.open_tumblr_settings)
        open_tumblr_settings_btn.grid(row=0, column=0)
        toggle_tumblr_btn = tk.Button(tumblr_btns, text='toggle')
        toggle_tumblr_btn.config(command=self.toggle_tumblr)
        toggle_tumblr_btn.grid(row=0, column=1)

        # Twitter
        twitter_frame = tk.Frame(right_frame)
        twitter_frame.pack(pady=5)
        twitter_label = tk.Label(twitter_frame, text='Twitter')
        twitter_label.pack()
        self.twitter_enabled = app_settings['twitter']['enabled']
        self.twitter_status_label = tk.Label(
            twitter_frame,
            text='Enabled: %s' % self.twitter_enabled,
            bg='green' if self.twitter_enabled else 'red')
        self.twitter_status_label.pack()
        twitter_btns = tk.Frame(twitter_frame)
        twitter_btns.pack()
        open_twitter_settings_btn = tk.Button(twitter_btns, text='config')
        open_twitter_settings_btn.config(command=self.open_twitter_settings)
        open_twitter_settings_btn.grid(row=0, column=0)
        toggle_twitter_btn = tk.Button(twitter_btns, text='toggle')
        toggle_twitter_btn.config(command=self.toggle_twitter)
        toggle_twitter_btn.grid(row=0, column=1)

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
        print('Export directory changed ~ ' + destination_folder)

        app_settings = get_settings()
        app_settings['all']['export_directory'] = destination_folder
        etc.export_settings(etc.DEFAULT_SETTINGS_PATH, app_settings)

    def request_scrape(self):
        global EXPORT_DIRECTORY
        global REQUEST_SCRAPE
        global SCRAPE_RANGE

        app_settings = get_settings()

        # Calculate SCRAPE_RANGE
        SCRAPE_RANGE = 1
        scan_selection = self.scrape_range_var.get()
        if scan_selection == ScrapeRange.SINCE_LAST:
            # Read date of last scrape from settings
            last_scrape_on = app_settings['all'].get('last_scrape_date')
            if last_scrape_on is not None:
                # Converts last scrape on to datetime object and finds the
                # difference between then and now.
                time_since_last = datetime.now() \
                    - datetime.strptime(last_scrape_on, '%Y-%m-%d')
                # Sets the SCRAPE_RANGE to the time difference IN DAYS
                SCRAPE_RANGE = time_since_last.days
            else:
                print("[ERROR] Please specify a valid time range.")
                return
        elif scan_selection == ScrapeRange.ONE_WEEK:
            SCRAPE_RANGE = 7
        elif scan_selection == ScrapeRange.CUSTOM:
            try:
                SCRAPE_RANGE = int(self.scrape_range_custom_entry.get())
                REQUEST_SCRAPE = True
            except ValueError:
                print('[ERROR] Please specify a valid custom scrape range.')
                return

        EXPORT_DIRECTORY = self.export_directory
        REQUEST_SCRAPE = True

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
                        {
                            'name': se_name.get(),
                            'min_karma': int(se_karma.get())
                        }
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

    def open_tumblr_settings(self):
        pass

    def open_twitter_settings(self):
        app_settings = get_settings()

        diag = tk.Toplevel()
        diag.wm_title("Twitter settings")

        tk.Label(diag, text="Profiles").pack()

        # Add profile editting frame
        profiles_frame = tk.Frame(diag)
        profiles_frame.pack()

        # get "topics" from app settings
        profile_data = app_settings['twitter']['users']

        # A list containing references to each entry.
        profile_entries = []
        row_x = 0
        for profile_no in profile_data:
            profile_entry = tk.Entry(profiles_frame)
            profile_entry.insert(0, profile_no)
            profile_entry.grid(row=row_x, column=0)
            profile_entries.append(profile_entry)
            row_x += 1

        # add profile
        def add_profile():
            nonlocal profile_entries

            # row index to insert into
            row = len(profile_entries)

            pending = tk.Entry(profiles_frame)
            pending.grid(row=row, column=0)
            profile_entries.append(pending)

        # remove profile
        def remove_profile():
            pass

        # Manip buttons
        edit_buttons = tk.Frame(diag)
        edit_buttons.pack()
        add_btn = tk.Button(edit_buttons, text='Add', command=add_profile)
        add_btn.grid(row=100, column=0)

        # Apply settings
        def apply_settings():
            nonlocal app_settings

            print(profile_entries)

            profiles = []
            for profile_entry in profile_entries:
                if profile_entry.get().strip():
                    profiles.append(profile_entry.get())

            app_settings['twitter']['users'] = profiles
            etc.export_settings(etc.DEFAULT_SETTINGS_PATH, app_settings)

            diag.destroy()

        # Add final buttons
        exit_buttons = tk.Frame(diag)
        exit_buttons.pack(side='bottom')
        apply_btn = tk.Button(exit_buttons, text="Apply",
                              command=apply_settings)
        apply_btn.grid(row=0, column=0)
        cancel_btn = tk.Button(exit_buttons, text='Cancel',
                               command=diag.destroy)
        cancel_btn.grid(row=0, column=1)

    def toggle_backend(self, enabled, setting_name, label):
        if enabled:
            status = 'Enabled: True'
            color = 'green'
            print('Backend enabled: ' + setting_name)
        else:
            status = 'Enabled: False'
            color = 'red'
            print('Backend disabled: ' + setting_name)

        label.config(text=status, bg=color)

        app_settings = get_settings()
        app_settings[setting_name]['enabled'] = enabled
        etc.export_settings(etc.DEFAULT_SETTINGS_PATH, app_settings)

    def toggle_reddit(self):
        self.reddit_enabled = not self.reddit_enabled
        self.toggle_backend(
            self.reddit_enabled, 'reddit', self.reddit_status_label)

    def toggle_TIG(self):
        self.TIG_enabled = not self.TIG_enabled
        self.toggle_backend(
            self.TIG_enabled, 'tigsource', self.TIG_status_label)

    def toggle_tumblr(self):
        self.tumblr_enabled = not self.tumblr_enabled
        self.toggle_backend(
            self.tumblr_enabled, 'tumblr', self.tumblr_status_label)

    def toggle_twitter(self):
        self.twitter_enabled = not self.twitter_enabled
        self.toggle_backend(
            self.twitter_enabled, 'twitter', self.twitter_status_label)


class StdoutRedirector(object):
    '''Redirect all print statements to a textarea. Used by MainApplication.'''
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert(tk.END, string)
        self.text_space.update()


def run_app():
    # Load configuration
    config = etc.retrieve_JSON('config.json')

    # Load settings file
    settings = change_settings(config['settings_path'])
    if settings is None:
        print("ERROR: Settings not found")
        return

    # Create root tkinter
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
