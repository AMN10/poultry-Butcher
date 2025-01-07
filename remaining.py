import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style  # استيراد Style من ttkbootstrap
import sqlite3
from datetime import datetime

# تحديد مسار قاعدة البيانات في مجلد المستخدم
db_path = Path.home() / "باقي المجذر.db"

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

# إنشاء جدول في قاعدة البيانات إذا لم يكن موجودًا
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    weight REAL NOT NULL,
    price REAL NOT NULL,
    total REAL NOT NULL,
    date TEXT NOT NULL
)
''')
conn.commit()

# الأصناف الأساسية
الأصناف_الأساسية = [
    "شاورما", "شيش", "فراخ صندوق (شوايه)", "اجنحه", 
    "صدور مخليه (بانيه)", "كبد وقوانص", "كوردن بلو", 
    "استربس", "شيش طاووق", "حمام كداب", 
    "هياكل (جناح ورقبه)", "هياكل عضم", "فراخ زبون", "قطاعي"
]


class RemainingWindow:
    def __init__(self, frame, return_to_main, root):
        self.frame = frame
        self.return_to_main = return_to_main
        self.root = root  # تخزين root كمتغير في الكلاس
        self.edit_popup = None  # لتعقب نافذة التعديل الحالية
        self.selected_category = tk.StringVar()  # المتغير الذي سيخزن المصنف المختار


        self.show_remaining_window()

    def show_remaining_window(self):
        self.clear_frame()  # حذف محتويات الإطار
        tk.Label(self.frame, text="محتويات باقي المجذر", font=("Helvetica", 14, "bold")).pack(pady=20)

        back_button = ttk.Button(self.frame, text="رجوع", command=self.return_to_main)
        back_button.pack(pady=10)

        self.show_sales_window()

    def show_sales_window(self):
        self.clear_frame()  # حذف محتويات الإطار
        tk.Label(self.frame, text="باقي المجذر", font=("Helvetica", 25, "bold")).pack(pady=20)

        # إضافة Label للتاريخ ووقت
        self.date_label = tk.Label(self.frame, text="", font=("Helvetica", 12))
        self.date_label.pack(pady=5)
        
        self.time_label = tk.Label(self.frame, text="", font=("Helvetica", 12))
        self.time_label.pack(pady=5)

        self.update_date_time()  # تحديث الوقت والتاريخ عند عرض النافذة

        # إعداد إطار واحد للمحتوى
        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

         # إعداد ttk.OptionMenu للأصناف
        self.selected_category.set("اختر مصنف")  # القيمة الافتراضية
        self.category_menu = ttk.OptionMenu(self.frame, self.selected_category, *الأصناف_الأساسية, command=self.select_category)
        self.category_menu.pack(pady=10)

        # إعداد زر عرض الكل
        show_all_button = ttk.Button(main_frame, text="عرض الكل", command=self.load_data_from_database)
        show_all_button.pack(pady=5)  # الزر داخل إطار المحتوى
        
        # إعداد الجدول
        self.columns = ("المصنف", "الوزن", "السعر", "الإجمالي", "التاريخ")
        self.tree = ttk.Treeview(main_frame, columns=self.columns, show="headings", height=6 )
        self.tree.pack(expand=True, fill="both", padx=20, pady=0)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")  # زيادة عرض الأعمدة
            self.tree.heading(col, text=col, anchor='center')  # محاذاة العناوين في الوسط

       # تغيير حجم الخط وارتفاع الصفوف
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 15, "bold"), rowheight=30)  # حجم خط أكبر وارتفاع صفوف أكبر

        self.tree.update_idletasks()  # تحديث العرض ليتناسب مع الإعدادات
        
        
        # إضافة Label لرصيد المجمد
        self.balance_label = tk.Label(self.frame, text="الرصيد المجمد: 0.0", font=("Helvetica", 20 , "bold"), fg="dark blue")
        self.balance_label.pack(pady=10)

        # ملء الجدول بالبيانات من قاعدة البيانات
        self.load_data_from_database()

        # إضافة حدث عند النقر على صف لتعديل الوزن والسعر
        self.tree.bind("<Double-1>", self.edit_row)

        # إضافة حدث للضغط على زر Delete لحذف الصف
        self.tree.bind("<Delete>", self.delete_selected_row)

        # إضافة حدث لفتح نافذة التعديل عند الضغط على Enter
        self.tree.bind("<Return>", self.edit_row)

        # ربط مفتاح المسطرة بالنافذة الرئيسية
        self.root.bind("<space>", self.select_row_with_space)

      

    def show_dropdown(self):
        # إنشاء قائمة منسدلة
        menu = tk.Menu(self.frame, tearoff=0)
        
        # إضافة الأصناف الأساسية إلى القائمة
        for category in الأصناف_الأساسية:
            menu.add_command(label=category, command=lambda c=category: self.select_category(c))

        # عرض القائمة المنسدلة أسفل الزر
        menu.post(self.selected_category.winfo_rootx(), self.selected_category.winfo_rooty() + self.category_button.winfo_height())

    def select_category(self, category):
       self.selected_category.set(category)  # تحديث المصنف المختار
       # إضافة المصنف تلقائيًا إلى الجدول
       self.add_selected_category()  # استدعاء دالة لإضافة المصنف

    def load_data_from_database(self):
        # حذف الصفوف التي إجماليها 0
        cursor.execute("DELETE FROM sales WHERE total = 0")
        conn.commit()

        cursor.execute("SELECT category, weight, price, total, date FROM sales ORDER BY total DESC")
        self.rows = cursor.fetchall()

        # تفريغ خانة المصنف عند الضغط على عرض الكل
        self.selected_category.set("اختر مصنف")

        self.update_treeview(self.rows)
        self.update_balance()  # تحديث الرصيد المجمد

    def update_treeview(self, rows):
        # مسح الجدول الحالي
        self.tree.delete(*self.tree.get_children())

        # ملء الجدول
        for row in rows:
            self.tree.insert("", tk.END, values=row, tags=('font',))

    def update_balance(self):
        total_balance = sum(row[3] for row in self.rows)  # جمع الأعمدة الخاصة بالإجمالي
        self.balance_label.config(text=f"الرصيد المجمد: {total_balance:.2f}")  # تحديث النص

    def filter_table(self, event=None):
        selected_category = self.selected_category.get()
        if selected_category == "":
            self.update_treeview(self.rows)  # عرض جميع البيانات إذا لم يتم اختيار مصنف
        else:
            filtered_rows = [row for row in self.rows if row[0] == selected_category]
            self.update_treeview(filtered_rows)

    def add_selected_category(self):
        selected_category = self.selected_category.get()
        if selected_category:
            # البحث عن الصف المحدد في الجدول
            for item in self.tree.get_children():
                item_values = self.tree.item(item)["values"]
                if item_values[0] == selected_category:
                    # إذا كان المصنف موجودًا بالفعل، نقوم بتحديث الوزن والسعر
                    self.show_edit_popup(item_values, item)
                    return

            # إذا كان المصنف غير موجود، نقوم بإضافة صف جديد
            today_date = datetime.now().strftime("%Y-%m-%d")  # صيغة التاريخ: YYYY-MM-DD
            cursor.execute("INSERT INTO sales (category, weight, price, total, date) VALUES (?, ?, ?, ?, ?)",
                           (selected_category, 0.0, 0.0, 0.0, today_date))
            conn.commit()  # حفظ التغييرات في قاعدة البيانات

            self.tree.insert("", tk.END, values=(selected_category, 0.0, 0.0, 0.0, today_date), tags=('font',))
            messagebox.showinfo("نجاح", f"تم إضافة المصنف: {selected_category}")

            # فتح نافذة التعديل لهذا المصنف الجديد تلقائيًا
            self.show_edit_popup((selected_category, 0.0, 0.0, 0.0, today_date), selected_category)
            # تفريغ خانة المصنف
            self.selected_category.set("اختر مصنف")  # إعادة تعيين القيمة إلى القيمة الافتراضية
        else:
            messagebox.showwarning("تحذير", "يرجى اختيار مصنف.")
            
    def edit_row(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "يرجى اختيار صف لتعديله.")
            return  # إذا لم يتم اختيار أي صف، لا نفعل شيئًا

        item_values = self.tree.item(selected_item)["values"]
        self.show_edit_popup(item_values, selected_item)

    def show_edit_popup(self, item_values, selected_item):
        # إذا كانت نافذة التعديل مفتوحة بالفعل، لا تفتح واحدة جديدة
        if self.edit_popup and self.edit_popup.winfo_exists():
            self.edit_popup.lift()  # ترفع النافذة الحالية للأمام إذا كانت موجودة
            return
        
        def submit_edit():
            try:
                new_weight = float(weight_entry.get())
                new_price = float(price_entry.get())
                if new_weight < 0 or new_price < 0:
                    raise ValueError("يجب إدخال قيم صحيحة.")

                total = new_weight * new_price  # حساب الإجمالي
                current_date = datetime.now().strftime("%Y-%m-%d")  # التاريخ الحالي

                # تحديث بيانات قاعدة البيانات
                cursor.execute("UPDATE sales SET weight = ?, price = ?, total = ?, date = ? WHERE category = ?",
                               (new_weight, new_price, total, current_date, item_values[0]))
                conn.commit()  # حفظ التغييرات
                self.load_data_from_database()  # تحديث الجدول بعد التعديل
                self.edit_popup.destroy()  # إغلاق النافذة بعد التعديل
            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال قيم صحيحة.")

        # إنشاء نافذة جديدة
        self.edit_popup = tk.Toplevel(self.frame)
        self.edit_popup.title("تعديل بيانات المصنف")
        # تعيين الأيقونة باستخدام مسار نسبي
        icon_path = Path(__file__).parent /"chicken.ico"  # مسار نسبي للأيقونة
        self.edit_popup.iconbitmap(str(icon_path))


        tk.Label(self.edit_popup, text="الوزن:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.edit_popup, text="السعر:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)

        weight_entry = tk.Entry(self.edit_popup)
        weight_entry.insert(0, item_values[1])  # الوزن الحالي
        weight_entry.grid(row=0, column=1, padx=10, pady=10)
        weight_entry.focus_set()  # وضع التركيز على خانة الوزن

        price_entry = tk.Entry(self.edit_popup)
        price_entry.insert(0, item_values[2])  # السعر الحالي
        price_entry.grid(row=1, column=1, padx=10, pady=10)
         # إضافة حدث للضغط على Enter للانتقال إلى حقل السعر
        weight_entry.bind("<Return>", lambda event: price_entry.focus_set())

        submit_button = ttk.Button(self.edit_popup, text="تعديل", command=submit_edit, style='success.TButton')
        submit_button.grid(row=2, columnspan=2, pady=10)
        # إضافة حدث للضغط على Enter في حقل السعر لتأكيد التعديل
        price_entry.bind("<Return>", lambda event: submit_edit())


        weight_entry.bind("<Down>", lambda event: price_entry.focus_set())
        price_entry.bind("<Up>", lambda event: weight_entry.focus_set())

        self.edit_popup.transient(self.frame)  # اجعل النافذة فرعية للنافذة الأصلية
        self.edit_popup.grab_set()  # اجعل النافذة فعالة

    def delete_selected_row(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "يرجى اختيار صف لحذفه.")
            return  # إذا لم يتم اختيار أي صف، لا نفعل شيئًا

        item_values = self.tree.item(selected_item)["values"]
        category_to_delete = item_values[0]

        confirmation = messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد أنك تريد حذف '{category_to_delete}'؟")
        if confirmation:
            cursor.execute("DELETE FROM sales WHERE category = ?", (category_to_delete,))
            conn.commit()  # حفظ التغييرات في قاعدة البيانات
            self.load_data_from_database()  # تحديث الجدول بعد الحذف

    def update_date_time(self):
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
    
        # التحقق مما إذا كانت العناصر لا تزال موجودة
        if self.date_label.winfo_exists():
            self.date_label.config(text=f"التاريخ: {current_date}")  # تحديث تاريخ اليوم
        if self.time_label.winfo_exists():
            self.time_label.config(text=f"الوقت: {current_time}")  # تحديث الوقت
    
        # إعادة تعيين الدالة كل ثانية
        self.frame.after(1000, self.update_date_time)

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()  # حذف جميع العناصر في الإطار

    def select_row_with_space(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.edit_row(event)  # استدعاء تعديل الصف عند الضغط على مسطرة

if __name__ == "__main__":
    root = tk.Tk()
    root.title("نظام إدارة المبيعات")
    root.geometry("800x600")

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    remaining_window = RemainingWindow(main_frame, root.quit, root)  # تمرير root هنا

    root.mainloop()
