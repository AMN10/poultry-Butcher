import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import ttk
import sqlite3
from datetime import datetime

class EmployeesTable:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.create_table()  # استدعاء دالة إنشاء الجدول
        self.create_employees_table()
        self.edit_window = None  # متغير لتتبع نافذة التعديل

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    salary REAL NOT NULL,
                    date TEXT NOT NULL
                )
            ''')

    def create_employees_table(self):
        # إنشاء إطار لجدول الموظفين
        self.employees_frame = tk.Frame(self.parent)
        self.employees_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        # عنوان الجدول
        employees_label = tk.Label(self.employees_frame, text="الموظفين", font=("Helvetica", 16))
        employees_label.pack(pady=10)

        # إطار للصف الخاص بإدخال الموظف
        input_frame = tk.Frame(self.employees_frame)
        input_frame.pack(pady=5)

        # إضافة Label فوق خانة إدخال اسم الموظف
        name_label = tk.Label(input_frame, text="اسم الموظف:")
        name_label.grid(row=0, column=1)

        # خانة إدخال اسم الموظف
        self.name_entry = ttk.Entry(input_frame, width=20)
        self.name_entry.grid(row=1, column=1, pady=1, padx=5)
        self.name_entry.bind("<Return>", lambda event: self.salary_entry.focus_set())  # التركيز على خانة الماء عند الضغط على السهم اليمين
        self.name_entry.bind("<Left>", lambda event: self.salary_entry.focus_set())  # التركيز على خانة الماء عند الضغط على السهم اليمين

        # إضافة Label فوق خانة إدخال راتب الموظف
        salary_label = tk.Label(input_frame, text="راتب الموظف:")
        salary_label.grid(row=0, column=0)

        # خانة إدخال راتب الموظف
        self.salary_entry = ttk.Entry(input_frame, width=20)
        self.salary_entry.grid(row=1, column=0, pady=1, padx=5)
        self.salary_entry.bind("<Return>", lambda event: self.add_employee())  # التركيز على خانة الماء عند الضغط على السهم اليمين
        self.salary_entry.bind("<Right>", lambda event: self.name_entry.focus_set())  # التركيز على خانة الماء عند الضغط على السهم اليمين


        # زر لإضافة الموظف
        add_employee_button = ttk.Button(self.employees_frame, text="إضافة موظف", command=self.add_employee)
        add_employee_button.pack(pady=5)

        # إنشاء جدول الموظفين
        self.employees_table = ttk.Treeview(self.employees_frame, columns=("id", "name", "salary", "date"), show="headings", height=5)
        self.employees_table.heading("id", text="ID")
        self.employees_table.heading("name", text="الاسم")
        self.employees_table.heading("salary", text="الراتب")
        self.employees_table.heading("date", text="التاريخ")

        # إعداد الأعمدة
        self.employees_table.column("id", width=50, anchor='center')  
        self.employees_table.column("name", width=150, anchor='center')  
        self.employees_table.column("salary", width=100, anchor='center')  
        self.employees_table.column("date", width=120, anchor='center')  

        # تغيير حجم الخط
        #self.employees_table.tag_configure('normal', font=("Helvetica", 12, "bold"))

        self.employees_table.pack(fill=tk.BOTH, expand=True)

        # إنشاء Label لإظهار مجموع الرواتب
        self.total_salary_label = tk.Label(self.employees_frame, text="مجموع الرواتب: 0", font=("Helvetica", 14, "bold"))
        self.total_salary_label.pack(pady=5)


        # إدخال البيانات من قاعدة البيانات
        self.load_employees_data()
        

        # تحديد الصف عند النقر عليه
        self.employees_table.bind('<ButtonRelease-1>', self.on_row_select)
        self.employees_table.bind('<Return>', self.open_edit_window)  # فتح نافذة التعديل عند الضغط على Enter
        self.employees_table.bind('<Double-1>', self.open_edit_window)  # فتح نافذة التعديل عند النقر المزدوج

        # متغيرات لتخزين البيانات المحددة
        self.selected_employee_id = None

    def on_row_select(self, event):
        # الحصول على الصف المحدد
        selected_item = self.employees_table.selection()
        if selected_item:
            values = self.employees_table.item(selected_item)['values']
            self.selected_employee_id = values[0]  # ID

    def load_employees_data(self, month=None, year=None):
        # تحميل بيانات الموظفين من قاعدة البيانات وإضافتها إلى الجدول
        cursor = self.conn.cursor()
        query = "SELECT * FROM employees"
        params = []
    
        # إذا تم توفير الشهر والسنة، قم بتعديل الاستعلام لتصفية النتائج
        if month and year:
            query += " WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?"
            params.extend([f"{month:02d}", str(year)])
    
        query += " ORDER BY id DESC"  # ترتيب حسب id تنازلي
        cursor.execute(query, params)
        employees_data = cursor.fetchall()
    
        # مسح البيانات الموجودة في الجدول
        self.employees_table.delete(*self.employees_table.get_children())
    
        total_salary = 0  # متغير لحساب مجموع الرواتب
    
        for emp in employees_data:
            self.employees_table.insert("", tk.END, values=emp, tags=('normal',))
            total_salary += emp[2]  # جمع قيمة الراتب
    
        # تحديث الـ Label الخاص بمجموع الرواتب
        self.total_salary_label.config(text=f"مجموع الرواتب: {total_salary:.2f}")

    def update_table_with_data(self, rows):
        # مسح البيانات الموجودة في الجدول
        self.employees_table.delete(*self.employees_table.get_children())

        # إضافة الصفوف الجديدة
        for emp in rows:
            self.employees_table.insert("", tk.END, values=emp)

    def filter_by_month_year(self, month, year):
        # استعلام SQL لتصفية الموظفين حسب الشهر والسنة
        query = '''
            SELECT * FROM employees
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        '''
        # تنفيذ الاستعلام والحصول على النتائج
        cursor = self.conn.cursor()
        cursor.execute(query, (f"{month:02d}", str(year)))
        rows = cursor.fetchall()

        # هنا يجب تحديث الجدول المعروض بالبيانات الجديدة
        self.update_table_with_data(rows)
        self.load_employees_data(month, year)

    def add_employee(self):
        # دالة لإضافة موظف جديد إلى قاعدة البيانات
        name = self.name_entry.get().strip()  # مسح المسافات الزائدة
        salary = self.salary_entry.get().strip()  # مسح المسافات الزائدة
        date = datetime.now().strftime("%Y-%m-%d")  # استخدم التاريخ الحالي
        month = datetime.now().strftime("%m")  # الحصول على الشهر الحالي
        year = datetime.now().strftime("%Y")  # الحصول على السنة الحالية
    
        # تحقق من أن الحقول ليست فارغة وأن الراتب صحيح
        if not name or not salary.replace('.', '', 1).isdigit():  
            messagebox.showwarning("تحذير", "يرجى إدخال اسم وراتب صحيحين.")
            return
    
        # تحقق مما إذا كان الموظف موجودًا بالفعل لنفس الشهر والسنة
        if self.employee_exists(month, year, name):
            messagebox.showerror("خطأ", "يوجد موظف بنفس الاسم لهذا الشهر والسنة.")
            return
    
        with self.conn:
            self.conn.execute("INSERT INTO employees (name, salary, date) VALUES (?, ?, ?)", 
                              (name, salary, date))
        self.load_employees_data()  # إعادة تحميل البيانات لعرض الموظف الجديد
        self.name_entry.delete(0, tk.END)  # مسح خانة الإدخال
        self.salary_entry.delete(0, tk.END)  # مسح خانة الإدخال
    
    def employee_exists(self, month, year, name):
        # دالة للتحقق مما إذا كان الموظف موجودًا لنفس الشهر والسنة
        query = '''
            SELECT COUNT(*) FROM employees
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ? AND name = ?
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (month, year, name))
        count = cursor.fetchone()[0]
        return count > 0  # إذا كانت القيمة أكبر من 0، فهذا يعني أن الموظف موجود


    def open_edit_window(self, event=None):
        # Dالة لفتح نافذة التعديل
        if self.selected_employee_id is not None:
            if self.edit_window is None or not self.edit_window.winfo_exists():  # تحقق مما إذا كانت النافذة مفتوحة بالفعل
                selected_item = self.employees_table.selection()[0]
                values = self.employees_table.item(selected_item)['values']
    
                self.edit_window = tk.Toplevel(self.parent)
                self.edit_window.title("تعديل الموظف")
                self.edit_window.geometry("300x200")
               # استخدام المسار النسبي للأيقونة
                base_path = Path(__file__).parent
                icon_path = base_path / "chicken.ico"
                if icon_path.exists():
                    self.edit_window.iconbitmap(icon_path)
                else:
                    print("Icon file not found")

    
                # حقل إدخال الاسم
                name_label = tk.Label(self.edit_window, text="اسم الموظف:")
                name_label.pack(pady=5)
    
                name_entry = ttk.Entry(self.edit_window, width=20)
                name_entry.insert(0, values[1])  # إدخال الاسم الحالي
                name_entry.pack(pady=5)
                name_entry.focus_set()  # التركيز على حقل إدخال الاسم عند فتح النافذة
                name_entry.bind("<Return>", lambda event: salary_entry.focus())

    
                # حقل إدخال الراتب
                salary_label = tk.Label(self.edit_window, text="راتب الموظف:")
                salary_label.pack(pady=5)
                
    
                salary_entry = ttk.Entry(self.edit_window, width=20)
                salary_entry.insert(0, values[2])  # إدخال الراتب الحالي
                salary_entry.pack(pady=5)
    
                # زر لحفظ التعديلات
                save_button = ttk.Button(self.edit_window, text="حفظ التعديلات", command=lambda: self.save_changes(name_entry.get(), salary_entry.get()))
                save_button.pack(pady=10)
    
                # تمرير التركيز إلى الزر عند الضغط على Enter في حقل الراتب
                salary_entry.bind("<Return>", lambda event: save_button.invoke())
                
                self.edit_window.protocol("WM_DELETE_WINDOW", self.on_edit_window_close)  # التعامل مع غلق النافذة
    

    def save_changes(self, name, salary):
        # دالة لحفظ التعديلات في قاعدة البيانات
        try:
            salary_value = float(salary)  # تحويل الراتب إلى عدد عشري
            if name:  # تحقق من أن الاسم ليس فارغًا
                with self.conn:
                    self.conn.execute("UPDATE employees SET name=?, salary=? WHERE id=?", (name, salary_value, self.selected_employee_id))
                self.load_employees_data()  # إعادة تحميل البيانات لعرض التحديثات
                self.edit_window.destroy()  # إغلاق نافذة التعديل
                self.edit_window = None  # إعادة تعيين المتغير
            else:
                messagebox.showwarning("تحذير", "يرجى إدخال اسم صحيح.")
        except ValueError:
            messagebox.showwarning("تحذير", "يرجى إدخال راتب صحيح.")

    def on_edit_window_close(self):
        # دالة للتعامل مع غلق نافذة التعديل
        self.edit_window.destroy()  # إغلاق النافذة
        self.edit_window = None  # إعادة تعيين المتغير

if __name__ == "__main__":
    root = tk.Tk()
    root.title("جدول الموظفين")
    root.geometry("600x400")

    # تحديد مسار ملف قاعدة البيانات في مجلد الـ home الخاص بالمستخدم
    home_directory = Path.home()
    db_path = home_directory / "payments.db"  # إنشاء المسار الكامل لملف قاعدة البيانات
    os.chmod(db_path, 0o600)  # تعيين أذونات القراءة والكتابة للمستخدم فقط


    conn = sqlite3.connect(db_path)  # الاتصال بقاعدة البيانات في مجلد الـ home
    EmployeesTable(root, conn)

    root.protocol("WM_DELETE_WINDOW", lambda: [conn.close(), root.destroy()])  # إغلاق قاعدة البيانات عند إغلاق التطبيق
    root.mainloop()
