import os
import sys
import ctypes
import tkinter as tk
from pathlib import Path
import ttkbootstrap as ttkb
from invoice import InvoiceWindow
from sales import SalesWindow
from login import LoginWindow
from remaining import RemainingWindow
from payments import PaymentsWindow
from revenues import RevenuesWindow
from debts import DebtsWindow  # استيراد نافذة المديونية
from notes import NotesWindow  # استيراد نافذة الملاحظات



class MainApp:
    def __init__(self, root):
        super().__init__()

        self.is_dark_theme = True  # الحالة الافتراضية للسمة
        self.style = ttkb.Style("darkly")  # تعيين السمة
        self.root = root
        self.root.title("مجذر فراخ")

        # الحصول على المسار الحالي للملف
        base_path = Path(__file__).parent
        icon_path = base_path / "chicken.ico"

        if icon_path.exists():
            self.root.iconbitmap(icon_path)
        else:
            print("Icon file not found")

        self.frame = tk.Frame(self.root, bg="#E0E0E0")
        self.frame.pack(fill="both", expand=True)

        # عرض واجهة تسجيل الدخول في البداية
        self.show_login_window()

    def show_login_window(self):
        self.clear_frame()
        login_window = LoginWindow(self.frame, self.on_login_success)

    def on_login_success(self):
        self.show_main_menu()

    def show_main_menu(self):
        self.clear_frame()

        header_frame = tk.Frame(self.frame, bg="#E0E0E0")
        header_frame.pack(fill="x", ipady=1, pady=1)

        # إضافة Checkbutton لتبديل السمة
        self.theme_var = tk.BooleanVar(value=self.is_dark_theme)
        self.theme_check = ttkb.Checkbutton(
            header_frame,
            text="DarkMode",
            variable=self.theme_var,
            bootstyle="round-toggle",
            command=self.toggle_theme
        )
        self.theme_check.pack(side="right", padx=0, pady=5)

        # إنشاء إطار مركزي للتبويبات
        tab_frame = tk.Frame(self.frame, bg="#E0E0E0")
        tab_frame.pack(fill="both", expand=True)

        # إنشاء التبويبات باستخدام ttk.Notebook
        self.notebook = ttkb.Notebook(tab_frame, bootstyle="dark")
        self.notebook.pack(fill="both", expand=True)

        # إنشاء التبويبات للصفحات المختلفة
        self.create_tabs()

        # إضافة محتوى كل تبويب
        self.show_invoice_window()
        self.show_sales_window()
        self.show_remaining_window()
        self.show_payments_window()
        self.show_revenues_window()
        self.show_debts_window()
        self.show_notes_window()  # إضافة محتوى تبويب الملاحظات

    def create_tabs(self):
        # إنشاء التبويبات
        self.invoice_tab = ttkb.Frame(self.notebook)
        self.sales_tab = ttkb.Frame(self.notebook)
        self.remaining_tab = ttkb.Frame(self.notebook)
        self.payments_tab = ttkb.Frame(self.notebook)
        self.revenues_tab = ttkb.Frame(self.notebook)
        self.debts_tab = ttkb.Frame(self.notebook)
        self.notes_tab = ttkb.Frame(self.notebook)

        # إضافة التبويبات إلى الـ Notebook
        self.notebook.add(self.invoice_tab, text="فاتورة الوارد")
        self.notebook.add(self.sales_tab, text="المبيعات")
        self.notebook.add(self.remaining_tab, text="باقي المجذر")
        self.notebook.add(self.payments_tab, text="المدفوعات")
        self.notebook.add(self.revenues_tab, text="الإيرادات")
        self.notebook.add(self.debts_tab, text="المديونية")
        self.notebook.add(self.notes_tab, text="الملاحظات")  # إضافة تبويب الملاحظات

    def show_notes_window(self):
        self.notes_window = NotesWindow(self.notes_tab)

    def toggle_theme(self):
        if self.is_dark_theme:
            self.style.theme_use("pulse")
            self.theme_check.config(text="LightMode")
            self.is_dark_theme = False
        else:
            self.style.theme_use("darkly")
            self.theme_check.config(text="DarkMode")
            self.is_dark_theme = True

    def show_invoice_window(self):
        InvoiceWindow(self.invoice_tab, self.show_main_menu)

    def show_sales_window(self):
        SalesWindow(self.sales_tab, self.show_main_menu)

    def show_remaining_window(self):
        RemainingWindow(self.remaining_tab, self.show_main_menu, self.root)

    def show_payments_window(self):
        PaymentsWindow(self.payments_tab, self.show_main_menu)

    def show_revenues_window(self):
        RevenuesWindow(self.revenues_tab, self.show_main_menu)

    def show_debts_window(self):
        DebtsWindow(self.debts_tab)

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    
        root = tk.Tk()
        app = MainApp(root)
        root.geometry("1250x670")
        root.mainloop()
