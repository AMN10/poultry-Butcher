import os
from pathlib import Path
import tkinter as tk
import sqlite3
from ttkbootstrap import Style, ttk
from datetime import datetime

class RevenuesWindow:
    def __init__(self, parent_frame, return_to_main):
        self.parent_frame = parent_frame
        self.return_to_main = return_to_main
        
        # تحديد مسارات قواعد البيانات في مجلد المستخدم
        self.invoices_db_path = Path.home() / "الفواتير.db"
        self.sales_db_path = Path.home() / "المبيعات.db"
        self.others_db_path = Path.home() / "باقي المجذر.db"
        self.payments_db_path = Path.home() / "payments.db"

        # Initialize database connections
        self.invoices_db = self.connect_to_db(self.invoices_db_path)
        self.sales_db = self.connect_to_db(self.sales_db_path)
        self.others_db = self.connect_to_db(self.others_db_path)
        self.payments_db = self.connect_to_db(self.payments_db_path)

        # إنشاء الجداول بعد إعداد قواعد البيانات
        self.create_tables()

        # الآن إنشاء نافذة الإيرادات بعد إعداد قواعد البيانات
        self.create_revenues_window()
        self.auto_update()  # بدء التحديث التلقائي

    def connect_to_db(self, db_path):
        """ الاتصال بقاعدة البيانات """
        try:
            # إذا لم يكن الملف موجودًا، قم بإنشائه
            if not db_path.exists():
                db_path.touch()
                print(f"تم إنشاء ملف قاعدة البيانات: {db_path}")

            connection = sqlite3.connect(db_path)
            print(f"تم الاتصال بقاعدة البيانات {db_path} بنجاح")
            return connection
        except sqlite3.Error as e:
            print(f"فشل الاتصال بقاعدة البيانات {db_path}. الخطأ: {e}")
            return None

    def create_tables(self):
        """ إنشاء الجداول اللازمة في قواعد البيانات المختلفة """
        # جدول الفواتير
        with self.invoices_db:
            self.invoices_db.execute('''
                CREATE TABLE IF NOT EXISTS فواتير (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    اسم_المورد TEXT,
                    الوزن REAL,
                    الوزن_الصافي REAL,
                    السعر REAL,
                    الهالك REAL,
                    الإجمالي REAL,
                    الإجمالي_قبل_الهالك REAL,
                    الفرق REAL,
                    التاريخ TEXT
                )
            ''')

        # جدول المبيعات
        with self.sales_db:
            self.sales_db.execute("""
                CREATE TABLE IF NOT EXISTS المصنفات (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    الاسم TEXT UNIQUE NOT NULL
                )
            """)
            self.sales_db.execute("""
                CREATE TABLE IF NOT EXISTS مبيعات (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    المصنف TEXT NOT NULL,
                    الوزن REAL NOT NULL,
                    السعر REAL NOT NULL,
                    الإجمالي REAL NOT NULL,
                    التاريخ TEXT NOT NULL,
                    الوقت TEXT NOT NULL
                )
            """)

        # جدول باقي المجذر
        with self.others_db:
            self.others_db.execute("""
                CREATE TABLE IF NOT EXISTS المصنفات (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    الاسم TEXT UNIQUE NOT NULL
                )
            """)
            self.others_db.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   category TEXT NOT NULL,
                   weight REAL NOT NULL,
                   price REAL NOT NULL,
                   total REAL NOT NULL,
                   date TEXT NOT NULL
                )
            """)

        # جدول المدفوعات
        with self.payments_db:
            self.payments_db.execute('''    
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    salary REAL NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
            self.payments_db.execute('''    
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    electricity REAL NOT NULL,
                    water REAL NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
    def format_currency(self, amount):
        """ تنسيق المبلغ إلى سلسلة مع الفواصل والعشري """
        return f"{amount:,.2f}"  # تنسيق إلى مكانين عشريين

    def create_revenues_window(self):
        """ إنشاء نافذة عرض الإيرادات """
        self.clear_frame()
        title_label = tk.Label(self.parent_frame, text="نافذة الإيرادات", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=20)

        # حساب وعرض الإيرادات
        daily_revenue = self.calculate_daily_revenue()
        monthly_revenue = self.calculate_monthly_revenue()
        annual_revenue = self.calculate_annual_revenue()
        frozen_balance = self.get_total_frozen_balance()

        # عرض الإيرادات بصيغة منسقة
        self.revenue_label = tk.Label(self.parent_frame, text=f"إيراد اليوم: {self.format_currency(daily_revenue)} ج", font=("Helvetica", 18, "bold"))
        self.revenue_label.pack(pady=20)

        self.revenue_label = tk.Label(self.parent_frame, text=f"إيراد الشهر: {self.format_currency(monthly_revenue)} ج", font=("Helvetica", 18, "bold"))
        self.revenue_label.pack(pady=20)

        self.revenue_label = tk.Label(self.parent_frame, text=f"إيراد السنة: {self.format_currency(annual_revenue)} ج", font=("Helvetica", 18, "bold"))
        self.revenue_label.pack(pady=20)

        self.frozen_balance_label = tk.Label(self.parent_frame, text=f"الرصيد المجمد من بواقي المجذر: {self.format_currency(frozen_balance)} ج", font=("Helvetica", 18, "bold"))
        self.frozen_balance_label.pack(pady=20)

    def auto_update(self):
        """ تحديث البيانات تلقائيًا كل 5 ثواني """
        self.create_revenues_window()  # تحديث العرض
        self.parent_frame.after(5000, self.auto_update)  # جدولة التحديث التالي بعد 5 ثواني


    def clear_frame(self):
        """ مسح جميع عناصر الإطار الحالي """
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

    def close_connections(self):
        """ إغلاق جميع اتصالات قواعد البيانات """
        if self.invoices_db:
            self.invoices_db.close()
        if self.sales_db:
            self.sales_db.close()
        if self.others_db:
            self.others_db.close()
        if self.payments_db:
            self.payments_db.close()
        print("تم إغلاق جميع اتصالات قواعد البيانات.")
        root.destroy()  # إغلاق النافذة

    def calculate_daily_revenue(self):
        """ حساب الإيرادات اليومية """
        today = datetime.now().strftime("%Y-%m-%d")
        total_invoices = self.get_total_from_invoices_day(today)
        total_sales = self.get_total_from_sales_day(today)
        daily_revenue = total_sales - total_invoices
        return daily_revenue

    def get_total_from_invoices_day(self, date):
        """ جلب الإجمالي من الفواتير لليوم """
        query = "SELECT SUM(الإجمالي_قبل_الهالك) FROM فواتير WHERE DATE(التاريخ) = ?"
        try:
            cursor = self.invoices_db.cursor()
            cursor.execute(query, (date,))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي الفواتير اليومية: {e}")
            return 0

    def get_total_from_sales_day(self, date):
        """ جلب الإجمالي من المبيعات لليوم """
        query = "SELECT SUM(الإجمالي) FROM مبيعات WHERE DATE(التاريخ) = ?"
        try:
            cursor = self.sales_db.cursor()
            cursor.execute(query, (date,))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي المبيعات اليومية: {e}")
            return 0

     
    def calculate_monthly_revenue(self):
        """ حساب الإيرادات الشهرية """
        today = datetime.now()
        first_day_of_month = today.replace(day=1)

        # حساب الإجمالي قبل الهالك من الفواتير خلال الشهر
        total_invoices = self.get_total_from_invoices_month(first_day_of_month)
        # حساب إجمالي المبيعات من المبيعات خلال الشهر
        total_sales = self.get_total_from_sales_month(first_day_of_month)
        # حساب إجمالي الرواتب من المدفوعات خلال الشهر
        total_salaries = self.get_total_salaries_month(first_day_of_month)
        # حساب إجمالي الفواتير من المدفوعات خلال الشهر
        total_bills = self.get_total_bills_month(first_day_of_month)

        # حساب الإيراد الشهري
        monthly_revenue = (total_sales) - (total_salaries + total_bills + total_invoices)

        return monthly_revenue

    def get_total_from_invoices_month(self, date):
        """ جلب الإجمالي قبل الهالك من جدول الفواتير خلال الشهر """
        query = "SELECT SUM(الإجمالي_قبل_الهالك) FROM فواتير WHERE DATE(التاريخ) >= ?"
        try:
            cursor = self.invoices_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي الفواتير الشهرية: {e}")
            return 0

    def get_total_from_sales_month(self, date):
        """ جلب الإجمالي من جدول المبيعات خلال الشهر """
        query = "SELECT SUM(الإجمالي) FROM مبيعات WHERE DATE(التاريخ) >= ?"
        try:
            cursor = self.sales_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي المبيعات الشهرية: {e}")
            return 0

    def get_total_salaries_month(self, date):
        """ جلب إجمالي الرواتب من جدول الموظفين خلال الشهر """
        query = "SELECT SUM(salary) FROM employees WHERE DATE(date) >= ?"
        try:
            cursor = self.payments_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي الرواتب الشهرية: {e}")
            return 0

    def get_total_bills_month(self, date):
        """ جلب إجمالي فواتير الكهرباء والماء خلال الشهر """
        query = "SELECT SUM(electricity + water) FROM bills WHERE DATE(date) >= ?"
        try:
            cursor = self.payments_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي الفواتير الشهرية: {e}")
            return 0

    def calculate_annual_revenue(self):
        """ حساب الإيرادات السنوية """
        today = datetime.now()
        first_day_of_year = today.replace(month=1, day=1)

        # حساب الإجمالي قبل الهالك من الفواتير خلال السنة
        total_invoices = self.get_total_from_invoices(first_day_of_year)
        # حساب إجمالي المبيعات من المبيعات خلال السنة
        total_sales = self.get_total_from_sales(first_day_of_year)
        # حساب إجمالي الرواتب من المدفوعات خلال السنة
        total_salaries = self.get_total_salaries(first_day_of_year)
        # حساب إجمالي الفواتير من المدفوعات خلال السنة
        total_bills = self.get_total_bills(first_day_of_year)

        # حساب الإيراد السنوي
        annual_revenue = (total_sales) - (total_salaries + total_bills + total_invoices)

        return annual_revenue

    def get_total_from_invoices(self, date):
        """ جلب الإجمالي قبل الهالك من جدول الفواتير خلال السنة """
        query = "SELECT SUM(الإجمالي_قبل_الهالك) FROM فواتير WHERE DATE(التاريخ) >= ?"
        try:
            cursor = self.invoices_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي الفواتير السنوية: {e}")
            return 0

    def get_total_from_sales(self, date):
        """ جلب الإجمالي من جدول المبيعات خلال السنة """
        query = "SELECT SUM(الإجمالي) FROM مبيعات WHERE DATE(التاريخ) >= ?"
        try:
            cursor = self.sales_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي المبيعات السنوية: {e}")
            return 0

    def get_total_salaries(self, date):
        """ جلب إجمالي الرواتب من جدول الموظفين خلال السنة """
        query = "SELECT SUM(salary) FROM employees WHERE DATE(date) >= ?"
        try:
            cursor = self.payments_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي الرواتب السنوية: {e}")
            return 0

    def get_total_bills(self, date):
        """ جلب إجمالي فواتير الكهرباء والماء خلال السنة """
        query = "SELECT SUM(electricity + water) FROM bills WHERE DATE(date) >= ?"
        try:
            cursor = self.payments_db.cursor()
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error as e:
            print(f"خطأ في جلب إجمالي الفواتير السنوية: {e}")
            return 0

    def get_total_frozen_balance(self):
        """ حساب الرصيد المجمد من جدول المبيعات """
        query = "SELECT SUM(total) FROM sales"
        cursor = self.others_db.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result[0] else 0


if __name__ == "__main__":
    root = tk.Tk()
    root.title("نافذة الإيرادات")
    root.geometry("800x600")

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    revenues_window = RevenuesWindow(main_frame, root.quit)

    root.protocol("WM_DELETE_WINDOW", revenues_window.close_connections)
    root.mainloop()
