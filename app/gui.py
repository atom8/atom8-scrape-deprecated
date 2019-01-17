import tkinter as tk
from tkinter import filedialog


APP_WIDTH = 960
APP_HEIGHT = 640


class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs),
        self.parent = parent

        # Left division
        left_frame = tk.Frame(self)
        left_frame.pack(side='left', fill='both', padx=10, pady=10)

        # Export destinaction
        export_frame = tk.Frame(left_frame)
        export_frame.pack()
        self.export_label = tk.Label(export_frame, text='Export to: ')
        self.export_label.pack(side='left', padx=10)
        tk.Button(export_frame, text='Browse',
                  command=self.do_change_destination_folder).pack(side='right')

        # Output diag
        output_frame = tk.Frame(left_frame)
        output_frame.pack(side='bottom', padx=10, pady=10)
        self.output = tk.Text(output_frame, height=10, width=40)
        self.output.insert(tk.END, 'Welcome to GDI scrape\n')
        self.output.pack(side='left', fill=tk.Y)
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
        perform_btn.config(command=self.do_perform_scrape)
        perform_btn.pack(side='bottom', padx=10, pady=10)

    def do_change_destination_folder(self):
        destination_folder = filedialog.askdirectory()
        self.export_label.config(text='Export to: ' + destination_folder)
        self.output.insert(tk.END, 'Export folder changed ~ %s\n' %
                           destination_folder)

    def do_perform_scrape(self):
        self.output.insert(tk.END, '*** SCRAPE STARTED ***\n')
        self.output.insert(tk.END, '*** SCRAPE COMPLETED ***\n')

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


def run_app():
    root = tk.Tk()
    root.title('GDI Scraper')
    # root.geometry('%sx%s' % (APP_WIDTH, APP_HEIGHT))

    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
