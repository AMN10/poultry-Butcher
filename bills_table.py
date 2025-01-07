import os
from pathlib import Path
import tkinter as tk
from ttkbootstrap import ttk
import sqlite3
from datetime import datetime
import tkinter.messagebox as messagebox
import re  # استيراد مكتبة التعبيرات العادية

class BillsTable:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.edit_window = None  # متغير لتتبع نافذة التعديل
        self.create_table()  # إنشاء الجدول إذا لم يكن موجودًا
        self.create_bills_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    electricity REAL NOT NULL,
                    water REAL NOT NULL,
                    date TEXT NOT NULL
                )
            ''')

    def create_bills_table(self):
        # إنشاء إطار لجدول الفواتير
        self.bills_frame = tk.Frame(self.parent)
        self.bills_frame.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        # عنوان الجدول
        bills_label = tk.Label(self.bills_frame, text="فواتير الكهرباء والماء", font=("Helvetica", 16))
        bills_label.pack(pady=10)

        # إنشاء إطار لتخطيط الخانات والأسماء في نفس الصف
        input_frame = tk.Frame(self.bills_frame)
        input_frame.pack(pady=5)

        # Label خانة إدخال فاتورة الكهرباء
        electricity_label = tk.Label(input_frame, text="فاتورة الكهرباء:")
        electricity_label.grid(row=0, column=0, padx=5)
        
        # خانة إدخال فاتورة الكهرباء
        self.electricity_entry = ttk.Entry(input_frame, width=20)
        self.electricity_entry.grid(row=1, column=0, padx=5)
        self.electricity_entry.bind("<Right>", lambda event: self.water_entry.focus_set())  # التركيز على خانة الماء عند الضغط على السهم اليمين
        self.electricity_entry.bind("<Left>", lambda event: self.electricity_entry.focus_set())  # التركيز مرة أخرى على خانة الكهرباء عند الضغط على السهم اليسار

        # Label خانة إدخال فاتورة الماء
        water_label = tk.Label(input_frame, text="فاتورة الماء:")
        water_label.grid(row=0, column=1, padx=5)

        # خانة إدخال فاتورة الماء
        self.water_entry = ttk.Entry(input_frame, width=20)
        self.water_entry.grid(row=1, column=1, padx=5)
        self.water_entry.bind("<Left>", lambda event: self.electricity_entry.focus_set())  # التركيز على خانة الكهرباء عند الضغط على السهم اليسار
        self.water_entry.bind("<Right>", lambda event: self.water_entry.focus_set())  # التركيز مرة أخرى على خانة الماء عند الضغط على السهم اليمين

        self.electricity_entry.bind("<Return>", lambda event: self.water_entry.focus_set())  # التركيز على خانة الماء عند الضغط على السهم اليمين
        self.water_entry.bind("<Return>", lambda event: add_bill_button.focus_set())  # التركيز مرة أخرى على خانة الماء عند الضغط على السهم اليمين

        # زر لإضافة الفاتورة
        add_bill_button = ttk.Button(self.bills_frame, text="إضافة فاتورة", command=self.add_bill)
        add_bill_button.pack(pady=5)

        self.water_entry.bind("<Return>", lambda event: self.electricity_entry.focus_set())  # التركيز على خانة الماء عند الضغط على السهم اليمين
        self.electricity_entry.bind("<Return>", lambda event: self.add_bill())  # التركيز مرة أخرى على خانة الماء عند الضغط على السهم اليمين

        

        # إنشاء جدول الفواتير مع تعيين الارتفاع
        self.bills_table = ttk.Treeview(self.bills_frame, columns=("id", "electricity", "water", "date"), show="headings", height=5)
        self.bills_table.heading("id", text="ID")
        self.bills_table.heading("electricity", text="فاتورة الكهرباء")
        self.bills_table.heading("water", text="فاتورة الماء")
        self.bills_table.heading("date", text="التاريخ")

        # إعداد الأعمدة
        self.bills_table.column("id", width=50, anchor='center')  
        self.bills_table.column("electricity", width=150, anchor='center')  
        self.bills_table.column("water", width=150, anchor='center')  
        self.bills_table.column("date", width=120, anchor='center')  

        self.bills_table.pack(fill=tk.BOTH, expand=True)
        self.bills_table.tag_configure('normal', font=("Helvetica", 12, "bold"))

         # مساحة لعرض المجموع أسفل الجدول
        self.total_label = tk.Label(self.bills_frame, text="مجموع الفواتير: 0.00", font=("Helvetica", 14, "bold"))
        self.total_label.pack(fill=tk.X, padx=20, pady=5)


        # إدخال البيانات من قاعدة البيانات
        self.load_bills_data()

        # إضافة حدث عند الضغط على مفتاح "Enter"
        self.bills_table.bind("<Return>", self.open_edit_window)

        # إضافة حدث عند النقر المزدوج
        self.bills_table.bind("<Double-1>", self.open_edit_window)

    def load_bills_data(self):
        # الحصول على الشهر والسنة الحاليين
        current_month = datetime.now().strftime("%m")
        current_year = datetime.now().strftime("%Y")

        # تحميل بيانات الفواتير من قاعدة البيانات للشهر والسنة الحاليين فقط
        cursor = self.conn.cursor()
        query = '''
            SELECT * FROM bills 
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
            ORDER BY id DESC
        '''
        cursor.execute(query, (current_month, current_year))
        bills_data = cursor.fetchall()

        # مسح جميع الصفوف الحالية من الجدول
        for row in self.bills_table.get_children():
            self.bills_table.delete(row)

        # إضافة البيانات الجديدة وحساب الإجماليات
        total_electricity = 0
        total_water = 0
        for bill in bills_data:
            self.bills_table.insert("", tk.END, values=bill)
            total_electricity += float(bill[1])
            total_water += float(bill[2])

        # حساب المجموع
        total_sum = total_electricity + total_water
        self.total_label.config(text=f"مجموع الفواتير لهذا الشهر: {total_sum:.2f}")  # تحديث المجموع المعروض

    def update_table_with_data(self, rows):
        # مسح البيانات الموجودة في الجدول
        self.bills_table.delete(*self.bills_table.get_children())

        # إضافة الصفوف الجديدة
        for bill in rows:
            self.bills_table.insert("", tk.END, values=bill)

    def filter_by_month_year(self, month, year):
        # فلترة الفواتير حسب الشهر والسنة
        query = '''
            SELECT * FROM bills
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (f"{month:02d}", str(year)))
        filtered_bills = cursor.fetchall()

        # مسح البيانات الحالية من الجدول
        self.bills_table.delete(*self.bills_table.get_children())

        # إضافة البيانات المفلترة الجديدة
        total_electricity = 0
        total_water = 0
        for bill in filtered_bills:
            self.bills_table.insert("", tk.END, values=bill)
            total_electricity += float(bill[1])
            total_water += float(bill[2])

        # تحديث المجموع
        total_sum = total_electricity + total_water
        self.total_label.config(text=f"مجموع الفواتير: {total_sum:.2f}")  # عرض مجموع الفواتير بعد الفلترة

    def add_bill(self):
        # دالة لإضافة فاتورة جديدة إلى قاعدة البيانات
        electricity = self.electricity_entry.get().strip()  # مسح المسافات الزائدة
        water = self.water_entry.get().strip()  # مسح المسافات الزائدة
        date = datetime.now().strftime("%Y-%m-%d")  # استخدم التاريخ الحالي
        month = datetime.now().strftime("%m")  # الحصول على الشهر الحالي
        year = datetime.now().strftime("%Y")  # الحصول على السنة الحالية

        # التحقق مما إذا كانت المدخلات أرقام فقط
        if not self.validate_input(electricity, water):
            return

        # التحقق مما إذا كانت الفاتورة موجودة بالفعل لنفس الشهر والسنة
        if self.bill_exists(month, year):
            messagebox.showerror("خطأ", "توجد فاتورة بالفعل لهذا الشهر والسنة.")
            return

        with self.conn:
            self.conn.execute("INSERT INTO bills (electricity, water, date) VALUES (?, ?, ?)", 
                              (electricity, water, date))
        self.load_bills_data()  # إعادة تحميل البيانات لعرض الفاتورة الجديدة
        self.electricity_entry.delete(0, tk.END)  # مسح خانة الإدخال
        self.water_entry.delete(0, tk.END)  # مسح خانة الإدخال

    def bill_exists(self, month, year):
        # دالة للتحقق مما إذا كانت فاتورة موجودة لنفس الشهر والسنة
        query = '''
            SELECT COUNT(*) FROM bills
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (month, year))
        count = cursor.fetchone()[0]
        return count > 0  # إذا كانت القيمة أكبر من 0، فهذا يعني أن الفاتورة موجودة

    def validate_input(self, electricity, water):
        # دالة للتحقق من صحة المدخلات
        decimal_pattern = re.compile(r'^\d+(\.\d+)?$')  # التعبير العادي للأرقام العشرية
        if not decimal_pattern.match(electricity):
            messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح في فاتورة الكهرباء.")
            return False
        if not decimal_pattern.match(water):
            messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح في فاتورة الماء.")
            return False
        return True

    def open_edit_window(self, event):
        selected_item = self.bills_table.selection()
        if selected_item:
            if self.edit_window is not None and self.edit_window.winfo_exists():
                return  # Prevent opening multiple edit windows

            values = self.bills_table.item(selected_item[0], 'values')

            # Create edit window
            self.edit_window = tk.Toplevel(self.parent)
            self.edit_window.title("تعديل فاتورة")
            # استخدام المسار النسبي للأيقونة
            base_path = Path(__file__).parent
            icon_path = base_path / "chicken.ico"
            if icon_path.exists():
                self.edit_window.iconbitmap(icon_path)
            else:
                print("Icon file not found")

            self.edit_window.geometry("300x200")

            # Electricity label and entry
            electricity_label = tk.Label(self.edit_window, text="فاتورة الكهرباء:")
            electricity_label.pack(pady=5)
            electricity_entry = ttk.Entry(self.edit_window, width=20)
            electricity_entry.insert(0, values[1])
            electricity_entry.pack(pady=5)

            # Water label and entry
            water_label = tk.Label(self.edit_window, text="فاتورة الماء:")
            water_label.pack(pady=5)
            water_entry = ttk.Entry(self.edit_window, width=20)
            water_entry.insert(0, values[2])
            water_entry.pack(pady=5)

            # Update button
            update_button = ttk.Button(self.edit_window, text="تحديث",
                                        command=lambda: self.update_bill(values[0], electricity_entry.get(), water_entry.get(), self.edit_window))
            update_button.pack(pady=10)

            # Set focus to the first entry
            electricity_entry.focus()

            # Binding Enter key to switch focus between fields
            def focus_next(event):
                if event.widget == electricity_entry:
                    water_entry.focus()
                elif event.widget == water_entry:
                    update_button.focus()
                else:
                    update_button.invoke()  # Simulate button click

            # Bind the Enter key to the focus_next function
            electricity_entry.bind('<Return>', focus_next)
            water_entry.bind('<Return>', lambda e: self.update_bill(values[0], electricity_entry.get(), water_entry.get(), self.edit_window))
            
            # Handle window close
            self.edit_window.protocol("WM_DELETE_WINDOW", self.on_edit_window_close)

    def on_edit_window_close(self):
        # دالة يتم استدعاؤها عند إغلاق نافذة التعديل
        self.edit_window.destroy()  # إغلاق نافذة التعديل
        self.edit_window = None  # إعادة تعيين المتغير إلى None

    def update_bill(self, bill_id, electricity, water, edit_window):
        # دالة لتحديث الفاتورة في قاعدة البيانات
        date = datetime.now().strftime("%Y-%m-%d")  # استخدم التاريخ الحالي

        # التحقق مما إذا كانت المدخلات أرقام فقط
        if not self.validate_input(electricity, water):
            return

        with self.conn:
            self.conn.execute("UPDATE bills SET electricity = ?, water = ?, date = ? WHERE id = ?", 
                              (electricity, water, date, bill_id))
        self.load_bills_data()  # إعادة تحميل البيانات لعرض الفاتورة الجديدة
        self.on_edit_window_close()  # إغلاق نافذة التعديل
if __name__ == "__main__":
    root = tk.Tk()
    root.title("جدول الفواتير")
    root.geometry("600x400")

     # تحديد مسار ملف قاعدة البيانات في مجلد الـ home الخاص بالمستخدم
    home_directory = Path.home()
    db_path = home_directory / "payments.db"  # إنشاء المسار الكامل لملف قاعدة البيانات
    os.chmod(db_path, 0o600)  # تعيين أذونات القراءة والكتابة للمستخدم فقط

    conn = sqlite3.connect(db_path)  # الاتصال بقاعدة البيانات في مجلد الـ home
    BillsTable(root, conn)


    root.mainloop()
