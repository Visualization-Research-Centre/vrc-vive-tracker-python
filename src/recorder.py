import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")

        self.record_path = tk.StringVar()
        self.load_path = tk.StringVar()
        self.play_path = tk.StringVar()

        # Record Button and Entry
        self.record_button = tk.Button(root, text="Record", command=self.record)
        self.record_button.grid(row=0, column=0, padx=10, pady=10)

        self.record_entry = tk.Entry(root, textvariable=self.record_path, state='readonly')
        self.record_entry.grid(row=0, column=1, padx=10, pady=10)

        # Load Button and Entry
        self.load_button = tk.Button(root, text="Load", command=self.load)
        self.load_button.grid(row=1, column=0, padx=10, pady=10)

        self.load_entry = tk.Entry(root, textvariable=self.load_path, state='readonly')
        self.load_entry.grid(row=1, column=1, padx=10, pady=10)

        # Play Button and Entry
        self.play_button = tk.Button(root, text="Play", command=self.play)
        self.play_button.grid(row=2, column=0, padx=10, pady=10)

        self.play_entry = tk.Entry(root, textvariable=self.play_path, state='readonly')
        self.play_entry.grid(row=2, column=1, padx=10, pady=10)

        # Get the directory of the current script
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

    def record(self):
        file_path = filedialog.asksaveasfilename(initialdir=self.project_dir, defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.record_path.set(file_path)
            self.play_path.set(file_path)  # Set the play path to the recorded file
            # Create and save the file
            with open(file_path, 'w') as file:
                file.write("This is a test recording.")
            messagebox.showinfo("Info", f"Recording saved at: {file_path}")

    def load(self):
        file_path = filedialog.askopenfilename(initialdir=self.project_dir, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.load_path.set(file_path)
            self.play_path.set(file_path)  # Set the play path to the loaded file
            messagebox.showinfo("Info", f"Loaded file: {file_path}")

    def play(self):
        if self.play_path.get():
            messagebox.showinfo("Info", f"Playing: {self.play_path.get()}")
        else:
            messagebox.showwarning("Warning", "No file loaded to play!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()
