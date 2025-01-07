import os
from pathlib import Path
import tkinter as tk
from ttkbootstrap import Style  # استيراد مكتبة ttkbootstrap
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from dateutil import parser  # استيراد مكتبة dateutil
# تحديد مسار قاعدة البيانات في مجلد المستخدم
db_path = Path.home() / "المبيعات.db"

# إذا لم يكن الملف موجودًا، قم بإنشائه
if not db_path.exists():
    # إنشاء الملف
    db_path.touch()
    print(f"تم إنشاء ملف قاعدة البيانات: {db_path}")

    # ضبط الأذونات لتمكين القراءة والكتابة
    os.chmod(db_path, 0o600)  # تعيين أذونات القراءة والكتابة للمستخدم فقط
    print(f"تم ضبط الأذونات لملف قاعدة البيانات: {db_path}")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect(db_path)
cursor = conn.cursor()  # تعريف الكائن cursor هنا

# Function to initialize the database
def initialize_database():
    cursor.execute("""
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
    conn.commit()


class ReportsWindow:
    def __init__(self, frame, return_to_sales):
        # إعداد السمة

        self.frame = frame
        self.return_to_sales = return_to_sales
        self.title_font = ("Helvetica", 14, "bold")
        self.show_reports_page()

    def show_reports_page(self):
        """عرض صفحة التقارير"""
        self.clear_frame()  # مسح محتويات الإطار الحالي
        
        # عنوان الصفحة
        title_label = ttk.Label(self.frame, text="التقارير الشهرية والسنوية", font=("Helvetica", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # زر عرض الحساب الشهري والسنوي تحت العنوان
        combined_button = ttk.Button(self.frame, text="عرض الحسابات الشهرية والسنوية", command=self.show_monthly_and_annual_totals, style="success.TButton")
        combined_button.grid(row=1, column=0, columnspan=2, pady=20)
        combined_button.config(width=30)
          # جعل التركيز على زر الحسابات الشهرية والسنوية
        combined_button.focus_set()

        # قائمة اختيار السنة من 2020 إلى 2100
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_button = ttk.OptionMenu(self.frame, self.year_var, self.year_var.get(), *[str(year) for year in range(2020, 2101)], command=lambda _: self.show_annual_total())
        year_button.grid(row=2, column=0, pady=10)

        # Label لعرض إجمالي الفواتير في السنة المختارة
        self.selected_year_total_label = tk.Label(self.frame, text="", font=("Helvetica", 15, "bold"), fg="blue")
        self.selected_year_total_label.grid(row=3, column=0, pady=10)

        # جدول السنة في النصف الأيسر
        self.columns_year = ("السنة", "إجمالي السنة", "إجمالي السنة الماضية", "المؤشر")
        self.tree_year = ttk.Treeview(self.frame, columns=self.columns_year, show="headings", height=6)
        self.tree_year.column("السنة", width=100, anchor="center")
        self.tree_year.column("إجمالي السنة", width=150, anchor="center")
        self.tree_year.column("إجمالي السنة الماضية", width=150, anchor="center")
        self.tree_year.column("المؤشر", width=180, anchor="center")

        for col in self.columns_year:
            self.tree_year.heading(col, text=col, anchor='center')

        self.tree_year.grid(row=4, column=0, pady=(10, 20))
         # إعداد الأسلوب للجدول
        style = ttk.Style()
        style.configure("Treeview",
                       
                        rowheight=40,  # التحكم في ارتفاع الصفوف
                        font=("Helvetica", 15 ,"bold"),
                        )
        
        style.map("Treeview",
                  background=[("selected", "lightblue")])

        # قائمة اختيار الشهر بالعربية
        arabic_months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", 
                         "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        self.month_var = tk.StringVar(value=f"{datetime.now().month} - {arabic_months[datetime.now().month - 1]}")
        month_button = ttk.OptionMenu(self.frame, self.month_var, self.month_var.get(), *[f"{i+1} - {month}" for i, month in enumerate(arabic_months)], command=lambda _: self.show_monthly_total())
        month_button.grid(row=2, column=1, pady=10)

        # Label لعرض إجمالي الفواتير في الشهر المختار
        self.selected_month_total_label = tk.Label(self.frame, text="", font=("Helvetica", 14, "bold"))
        self.selected_month_total_label.grid(row=3, column=1, pady=10)

        

        # جدول الشهر في النصف الأيمن
        self.columns_month = ("الشهر", "إجمالي الشهر", "إجمالي الشهر الماضي", "المؤشر")
        self.tree_month = ttk.Treeview(self.frame, columns=self.columns_month, show="headings", height=6)
        self.tree_month.column("الشهر", width=100, anchor="center")
        self.tree_month.column("إجمالي الشهر", width=150, anchor="center")
        self.tree_month.column("إجمالي الشهر الماضي", width=150, anchor="center")
        self.tree_month.column("المؤشر", width=180, anchor="center")

        for col in self.columns_month:
            self.tree_month.heading(col, text=col, anchor='center')

        self.tree_month.grid(row=4, column=1, pady=(10, 20))

        # تعيين أبعاد النسبة للجدولين
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # زر الرجوع في أسفل الصفحة
        back_button = ttk.Button(self.frame, text="رجوع", command=self.return_to_sales, style="danger.TButton")
        back_button.grid(row=5, column=0, columnspan=2, pady=20)

        combined_button.bind("<Down>", lambda e: year_button.focus_set())
        month_button.bind("<KeyPress-Left>", lambda e: year_button.focus_set())
        year_button.bind("<KeyPress-Right>", lambda e: month_button.focus_set())
        month_button.bind("<Up>", lambda e: combined_button.focus_set())
        month_button.bind("<Down>", lambda e: back_button.focus_set())
        back_button.bind("<Up>", lambda e: month_button.focus_set())
        year_button.bind("<Up>", lambda e: combined_button.focus_set())
        year_button.bind("<Down>", lambda e: back_button.focus_set())
        back_button.bind("<Up>", lambda e: year_button.focus_set())


    def show_monthly_and_annual_totals(self):
        """عرض مجموع الفواتير الشهري والسنوي في نفس الوقت."""
        self.show_monthly_total()
        self.show_annual_total()

   
    def show_monthly_total(self):
        """وظيفة لعرض مجموع إجمالي الفواتير للأشهر الخمسة الأخيرة مع مراعاة السنة."""
        # استخراج الرقم من السلسلة النصية
        month_string = self.month_var.get()
        if month_string:
            selected_month = int(month_string.split(" - ")[0])  # استخدم فقط الجزء الرقمي
        else:
            messagebox.showerror("خطأ", "يرجى اختيار شهر.")
            return
    
        selected_year = int(self.year_var.get())
    
        if selected_month < 1 or selected_month > 12:
            messagebox.showerror("خطأ", "يرجى اختيار شهر صحيح (1-12).")
            return
    
        self.tree_month.delete(*self.tree_month.get_children())
    
        total_month = 0
    
        for i in range(5):
            month_index = (selected_month - i - 1) % 12
            year_index = selected_year + (selected_month - i - 1) // 12
    
            # هنا نستخدم parser.parse لتحليل التواريخ من قاعدة البيانات
            start_date = f"{year_index}-{month_index + 1:02}-01"
            parsed_date = parser.parse(start_date)  # تحليل التاريخ باستخدام dateutil
    
            cursor.execute("SELECT SUM(الإجمالي) FROM مبيعات WHERE strftime('%Y-%m', التاريخ) = ?", 
                           (parsed_date.strftime('%Y-%m'),))  # استخدم التاريخ المحلل
            current_total = cursor.fetchone()[0] or 0
            total_month += current_total
    
            previous_month_index = (month_index - 1) % 12
            previous_year_index = year_index - (1 if month_index == 0 else 0)
    
            prev_start_date = f"{previous_year_index}-{previous_month_index + 1:02}-01"
            prev_parsed_date = parser.parse(prev_start_date)  # تحليل التاريخ للشهر الماضي
    
            cursor.execute("SELECT SUM(الإجمالي) FROM مبيعات WHERE strftime('%Y-%m', التاريخ) = ?", 
                           (prev_parsed_date.strftime('%Y-%m'),))  # استخدم التاريخ المحلل للشهر الماضي
            last_month_total = cursor.fetchone()[0] or 0
    
            difference = current_total - last_month_total
            indicator = "زيادة" if difference > 0 else "خسارة" if difference < 0 else "ثابت"
    
            color = "lightgreen" if difference > 0 else "red" if difference < 0 else "white"
            self.tree_month.insert("", "end", values=(f"{month_index + 1} - {year_index}", current_total, last_month_total, f"{difference:.2f} ({indicator})"), tags=(color,))
    
        self.tree_month.tag_configure("lightgreen", foreground="lightgreen")
        self.tree_month.tag_configure("red", foreground="red")
        self.tree_month.tag_configure("white", foreground="white")
    
        # تحديث الشريط ليظهر إجمالي الشهر المحدد
        month_name = self.month_var.get().split(" - ")[1]
        selected_month_total = [self.tree_month.item(child, 'values')[1] for child in self.tree_month.get_children() if f"{selected_month} - {selected_year}" in self.tree_month.item(child, 'values')[0]]
        total_selected_month = selected_month_total[0] if selected_month_total else 0
        self.selected_month_total_label.config(text=f"إجمالي الفواتير في شهر {month_name}: {total_selected_month}", fg="red")
   
    def show_annual_total(self):
        """وظيفة لعرض مجموع إجمالي الفواتير للسنوات الخمس الأخيرة."""
        selected_year = self.year_var.get()
    
        if len(selected_year) != 4 or not selected_year.isdigit():
            messagebox.showerror("خطأ", "يرجى إدخال سنة صحيحة (مثال: 2024).")
            return
    
        selected_year = int(selected_year)
    
        self.tree_year.delete(*self.tree_year.get_children())
    
        total_year = 0
    
        for i in range(5):
            year_date = str(selected_year - i)
            
            # جلب البيانات من قاعدة البيانات
            cursor.execute("SELECT التاريخ, SUM(الإجمالي) FROM مبيعات WHERE strftime('%Y', التاريخ) = ? GROUP BY التاريخ", (year_date,))
            records = cursor.fetchall()
    
            current_total = 0
    
            for record in records:
                التاريخ = record[0]
                الإجمالي = record[1]
    
                # تحليل التاريخ باستخدام parser.parse()
                try:
                    parsed_date = parser.parse(التاريخ)
                    if parsed_date.year == selected_year - i:
                        current_total += الإجمالي
                except ValueError:
                    messagebox.showerror("خطأ", "تاريخ غير صالح في قاعدة البيانات.")
                    return
    
            total_year += current_total
    
            # جلب البيانات للسنة الماضية
            cursor.execute("SELECT SUM(الإجمالي) FROM مبيعات WHERE strftime('%Y', التاريخ) = ?", (str(selected_year - i - 1),))
            last_year_total = cursor.fetchone()[0] or 0
    
            difference = current_total - last_year_total
            indicator = "زيادة" if difference > 0 else "خسارة" if difference < 0 else "ثابت"
    
            color = "lightgreen" if difference > 0 else "red" if difference < 0 else "white"
            self.tree_year.insert("", "end", values=(year_date, current_total, last_year_total, f"{difference:.2f} ({indicator})"), tags=(color,))
    
        self.tree_year.tag_configure("lightgreen", foreground="lightgreen")
        self.tree_year.tag_configure("red", foreground="red")
        self.tree_year.tag_configure("white", foreground="white")
    
        # تحديث الشريط ليظهر إجمالي السنة المختارة
        selected_year_total = [self.tree_year.item(child, 'values')[1] for child in self.tree_year.get_children() if str(selected_year) in self.tree_year.item(child, 'values')[0]]
        total_selected_year = selected_year_total[0] if selected_year_total else 0
        self.selected_year_total_label.config(text=f"إجمالي الفواتير في سنة {selected_year}: {total_selected_year}", fg="red")

    def clear_frame(self):
        """وظيفة لمسح جميع المحتويات الموجودة في الإطار الحالي"""
        for widget in self.frame.winfo_children():
            widget.destroy()


# تشغيل التطبيق
if __name__ == "__main__":
    root = tk.Tk()
    initialize_database()  # Ensure the database and table are initialized
    app = ReportsWindow(root, lambda: print("رجوع إلى المبيعات"))
    initialize_database()  # Ensure the database and table are initialized
    root.mainloop()
