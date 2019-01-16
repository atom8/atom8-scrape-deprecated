import tkinter as tk
from tkinter import filedialog


# tk.filedialog.askdirectory()


def get_destination():
    name = filedialog.askdirectory()
    print(name)


APP_WIDTH = 960
APP_HEIGHT = 640


class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs),
        self.parent = parent

        # Export destinaction
        export_frame = tk.Frame(self)
        export_frame.pack()
        self.export_label = tk.Label(export_frame, text='Export to: ')
        self.export_label.pack(side='left', padx=10)
        tk.Button(export_frame, text='Browse',
                  command=self.change_destination_folder).pack(side='right')

        # Console
        self.output = tk.Text(self, height=10, width=40)
        self.output.insert(tk.END, 'Welcome to GDI scraper')
        self.output.pack()

    def change_destination_folder(self):
        destination_folder = filedialog.askdirectory()
        self.export_label.config(text='Export to: ' + destination_folder)


if __name__ == '__main__':
    root = tk.Tk()
    # root.geometry('%sx%s' % (APP_WIDTH, APP_HEIGHT))

    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
