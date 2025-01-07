import tkinter as tk
from tkinter import ttk, messagebox, font  # استيراد وحدة الخط
import json
from ttkbootstrap import Style
from datetime import datetime

class NotesWindow:
    def __init__(self, parent):
        self.parent = parent
        self.notes = {}

        # إعداد خط كبير
        self.default_font = font.Font(size=12)  # يمكنك تغيير الرقم حسب الحاجة

        # Create the notebook to hold the notes
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Load saved notes
        self.load_notes()

        # Add New Note Button
        new_button = ttk.Button(self.parent, text="New Note", command=self.add_note, style="info.TButton")
        new_button.pack( padx=10, pady=10)

        # Add Delete Note Button
        delete_button = ttk.Button(self.parent, text="Delete Note", command=self.delete_note, style="danger.TButton")
        delete_button.pack(side=tk.BOTTOM, padx=10, pady=10)

    def load_notes(self):
        try:
            with open("notes.json", "r") as f:
                self.notes = json.load(f)

            for title, data in self.notes.items():
                self.create_note_tab(title, data["content"], data["date"])
        except FileNotFoundError:
            pass

    

    def create_note_tab(self, title, content, date):
        note_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(note_frame, text=title)

        # إعداد تخطيط العنوان
        title_label = ttk.Label(note_frame, text="Title:", font=self.default_font)
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="E")

        title_entry = ttk.Entry(note_frame, width=40, font=self.default_font)
        title_entry.insert(0, title)
        title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="W")

          # تركيز المؤشر على اسم الملاحظة
        title_entry.focus()
         # ربط حدث Enter للتنقل
        title_entry.bind("<Return>", lambda event: content_text.focus())

        content_label = ttk.Label(note_frame, text="Content:", font=self.default_font)
        content_label.grid(row=1, column=0, padx=10, pady=10, sticky="E")

        content_text = tk.Text(note_frame, width=60, height=10, font=self.default_font)
        content_text.insert(tk.END, content)
        content_text.grid(row=1, column=1, padx=10, pady=10, sticky="W")

        date_label = ttk.Label(note_frame, text=f"Date: {date}", font=self.default_font)
        date_label.grid(row=2, columnspan=2, padx=10, pady=10)

        # ربط حدث Enter للنص للتنقل إلى زر حفظ
        content_text.bind("<Return>", lambda event: save_button.invoke())

        save_button = ttk.Button(note_frame, text="Save", command=lambda: self.save_note(title, title_entry.get(), content_text.get("1.0", tk.END).strip()), style="primary.TButton")
        save_button.grid(row=3, columnspan=2, padx=10, pady=10)
        self.default_font = font.Font(size=13)  # تغيير الرقم حسب الحاجة
        # تكبير محتوى النص في الخانات
        for widget in note_frame.winfo_children():
            if isinstance(widget, (ttk.Entry, tk.Text)):
                widget.config(font=self.default_font)  # تطبيق حجم الخط على جميع خانات الإدخال

    def add_note(self):
        title = "New Note"
        content = ""
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.create_note_tab(title, content, date)

    def save_note(self, old_title, title, content):
        if old_title != title:
            self.notes.pop(old_title, None)  # Remove old title from notes
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes[title] = {"content": content, "date": date}

        try:
            with open("notes.json", "w") as f:
                json.dump(self.notes, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save notes: {e}")

        # Update the tab title
        current_tab = self.notebook.index(self.notebook.select())
        self.notebook.tab(current_tab, text=title)

    def delete_note(self):
        current_tab = self.notebook.index(self.notebook.select())
        note_title = self.notebook.tab(current_tab, "text")

        confirm = messagebox.askyesno("Delete Note", f"Are you sure you want to delete '{note_title}'?")
        if confirm:
            self.notebook.forget(current_tab)
            self.notes.pop(note_title, None)

            try:
                with open("notes.json", "w") as f:
                    json.dump(self.notes, f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save notes: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesWindow(root)
    root.geometry("1250x650")
    root.mainloop()
