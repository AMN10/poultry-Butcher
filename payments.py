from dateutil import parser  # استيراد مكتبة parser
from datetime import datetime  # تأكد من استيراد datetime
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from ttkbootstrap.widgets import DateEntry  # استيراد DateEntry
import sqlite3
from employees_table import EmployeesTable  # استيراد جدول الموظفين
from bills_table import BillsTable  # استيراد جدول الفواتير

class PaymentsWindow:
    def __init__(self, parent_frame, return_to_main):
        self.parent_frame = parent_frame
        self.return_to_main = return_to_main
        
        # تحديد مسار قاعدة البيانات في مجلد المستخدم
        db_path = Path.home() / "payments.db"
        
        # إذا لم يكن الملف موجودًا، قم بإنشائه
        if not db_path.exists():
            db_path.touch()
            print(f"تم إنشاء ملف قاعدة البيانات: {db_path}")
            os.chmod(db_path, 0o600)
            print(f"تم ضبط الأذونات لملف قاعدة البيانات: {db_path}")
        
        # الاتصال بقاعدة البيانات
        self.conn = sqlite3.connect(db_path)
        
        # إعداد نافذة المدفوعات
        self.create_payments_window()

    def create_tables(self):
        # إنشاء جدول الموظفين وفواتير الكهرباء والماء إذا لم تكن موجودة
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    salary REAL NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    electricity REAL NOT NULL,
                    water REAL NOT NULL,
                    date TEXT NOT NULL
                )
            ''')

    def create_payments_window(self):
        # مسح الإطار الحالي
        self.clear_frame()

        # عنوان نافذة المدفوعات
        title_label = tk.Label(self.parent_frame, text="نافذة المدفوعات", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=1)

        # إضافة خانة التاريخ
        date_label = tk.Label(self.parent_frame, text="اختر التاريخ:", font=("Helvetica", 14))
        date_label.pack(pady=1)

        self.date_entry = DateEntry(self.parent_frame, bootstyle='primary', width=12)  # إنشاء DateEntry
        self.date_entry.pack(pady=1)

        # زر الفلترة
        filter_button = ttk.Button(self.parent_frame, text="فلترة", command=self.filter_data,
                                   style="primary.TButton", padding=(10, 5))  # استخدام نمط زر
        filter_button.pack(pady=1)

        # إعداد شبكة (grid) للجداول
        tables_frame = tk.Frame(self.parent_frame)
        tables_frame.pack(fill=tk.BOTH, expand=True)

        # إنشاء كائن جدول الموظفين
        self.employees_table = EmployeesTable(tables_frame, self.conn)

        # إنشاء كائن جدول الفواتير
        self.bills_table = BillsTable(tables_frame, self.conn)

        # شريط عرض الإجمالي أسفل الجدول
        self.total_label = tk.Label(self.parent_frame, text="إجمالي الرواتب والفواتير: 0.00", 
                                    font=("Helvetica", 16, "bold"))
        self.total_label.pack(pady=5)

        # تحديث الإجمالي عند بداية البرنامج
        self.calculate_totals(datetime.today().month, datetime.today().year)

    def filter_data(self):
        # الحصول على التاريخ من DateEntry
        selected_date = self.date_entry.entry.get()
        
        # تحويل التاريخ إلى كائن datetime باستخدام parser.parse()
        try:
            date_object = parser.parse(selected_date)
        except ValueError:
            tk.messagebox.showerror("خطأ", "التاريخ غير صالح")
            return

        # الحصول على الشهر والسنة
        selected_month = date_object.month
        selected_year = date_object.year
        
        # فلترة الموظفين والفواتير حسب الشهر والسنة
        self.employees_table.filter_by_month_year(selected_month, selected_year)
        self.bills_table.filter_by_month_year(selected_month, selected_year)

        # تحديث الإجمالي بعد الفلترة
        self.calculate_totals(selected_month, selected_year)

    def calculate_totals(self, month, year):
        # حساب إجمالي الراتب للشهر والسنة المحددين
        cursor = self.conn.cursor()
        
        # جمع الرواتب
        cursor.execute('''
            SELECT SUM(salary) FROM employees 
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ''', (f"{month:02d}", str(year)))
        total_salary = cursor.fetchone()[0] or 0

        # جمع فواتير الكهرباء والماء
        cursor.execute('''
            SELECT SUM(electricity), SUM(water) FROM bills 
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ''', (f"{month:02d}", str(year)))
        total_electricity, total_water = cursor.fetchone()
        total_electricity = total_electricity or 0
        total_water = total_water or 0
        total_bills = total_electricity + total_water

        # حساب الإجمالي النهائي
        grand_total = total_salary + total_bills

        # تحديث شريط الإجمالي
        self.total_label.config(text=f"إجمالي الرواتب والفواتير: {grand_total:.2f}")

    def go_back(self):
        self.return_to_main()  # استدعاء الدالة للعودة إلى القائمة الرئيسية

    def clear_frame(self):
        # مسح جميع عناصر الإطار الحالي
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("نافذة المدفوعات")
    root.geometry("1000x700")  # زيادة حجم النافذة

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # تمرير دالة إغلاق التطبيق كإجراء العودة
    payments_window = PaymentsWindow(main_frame, root.quit)

    root.mainloop()
