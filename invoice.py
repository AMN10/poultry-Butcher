import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import date, datetime
from tkinter import font
from pathlib import Path
from ttkbootstrap import Style
from ttkbootstrap.widgets import DateEntry

# تحديد مسار قاعدة البيانات في مجلد المستخدم
db_path = Path.home() / "الفواتير.db"

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

# إنشاء/الاتصال بجدول الفواتير
cursor.execute('''
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
conn.commit()

class InvoiceWindow:
    def __init__(self, frame, return_to_main):
        self.frame = frame
        self.return_to_main = return_to_main
        self.title_font = ("Helvetica", 14, "bold")
        self.setup_invoice_window()

    def setup_invoice_window(self):
        self.clear_frame()
        tk.Label(self.frame, text="الفواتير", font=("Helvetica",25,"bold")).pack(pady=20)

        # إضافة خانة التاريخ باستخدام DateEntry من ttkbootstrap
        tk.Label(self.frame, text="اختر التاريخ:").pack(pady=5)
        self.date_entry = DateEntry(self.frame, bootstyle="success")  # إزالة date_pattern
        self.date_entry.pack(pady=5)

        # زر فلترة الفواتير
        filter_button = ttk.Button(self.frame, text="فلترة", command=self.filter_invoices_by_date)
        filter_button.pack(pady=10)
        
        # إنشاء إطار لتجميع المدخلات
        input_frame = tk.Frame(self.frame)
        input_frame.pack(pady=5)

        # تحديد حجم الخط
        large_font = font.Font(size=14)  # يمكنك تعديل الحجم كما تشاء
        
        # إضافة أسماء الخانات
        tk.Label(input_frame, text="الهالك (كجم):", font=large_font).grid(row=0, column=0, padx=5)
        tk.Label(input_frame, text="السعر (جنيه/كجم):", font=large_font).grid(row=0, column=2, padx=5)
        tk.Label(input_frame, text="الوزن (كجم):", font=large_font).grid(row=0, column=4, padx=5)
        tk.Label(input_frame, text="اسم المورد:", font=large_font).grid(row=0, column=6, padx=5)
        
        # إضافة حقول الإدخال
        self.entry_الهالك = tk.Entry(input_frame, font=large_font, width=8)
        self.entry_الهالك.grid(row=1, column=0, padx=5)
        
        self.entry_سعر = tk.Entry(input_frame, font=large_font, width=8)
        self.entry_سعر.grid(row=1, column=2, padx=5)
        
        self.entry_الوزن = tk.Entry(input_frame, font=large_font, width=8)
        self.entry_الوزن.grid(row=1, column=4, padx=5)
        
        self.entry_اسم_المورد = tk.Entry(input_frame, font=large_font, width=12)
        self.entry_اسم_المورد.grid(row=1, column=6, padx=5)
         # تركيز المؤشر في خانة اسم المورد
        self.entry_اسم_المورد.focus_set()  # تركيز المؤشر هنا
        

         # ربط مفتاح Enter للتنقل بين الحقول
        self.entry_اسم_المورد.bind("<Return>", lambda event: self.entry_الوزن.focus())
        self.entry_الوزن.bind("<Return>", lambda event: self.entry_سعر.focus())
        self.entry_سعر.bind("<Return>", lambda event: self.entry_الهالك.focus())
        self.entry_الهالك.bind("<Return>", lambda event: self.حساب_الإجمالي())
        # ربط مفاتيح الأسهم للتنقل أفقيًا
        self.entry_اسم_المورد.bind("<Left>", lambda event: self.entry_الوزن.focus())
        self.entry_الوزن.bind("<Left>", lambda event: self.entry_سعر.focus())
        self.entry_سعر.bind("<Left>", lambda event: self.entry_الهالك.focus())
        
        self.entry_الوزن.bind("<Right>", lambda event: self.entry_اسم_المورد.focus())
        self.entry_سعر.bind("<Right>", lambda event: self.entry_الوزن.focus())
        self.entry_الهالك.bind("<Right>", lambda event: self.entry_سعر.focus())
       

         # ربط مفاتيح الأسهم للتنقل عموديًا
        self.entry_اسم_المورد.bind("<Up>", lambda event: filter_button.focus())
        filter_button.bind("<Down>", lambda event: self.entry_اسم_المورد.focus())
        self.entry_اسم_المورد.bind("<Down>", lambda event: حساب_زر.focus())
        self.entry_الوزن.bind("<Down>", lambda event: حساب_زر.focus())
        self.entry_سعر.bind("<Down>", lambda event: حساب_زر.focus())
        self.entry_الهالك.bind("<Down>", lambda event: حساب_زر.focus())

        self.entry_الوزن.bind("<Up>", lambda event:filter_button.focus())
        self.entry_سعر.bind("<Up>", lambda event:filter_button.focus())
        self.entry_الهالك.bind("<Up>", lambda event:filter_button.focus())


        # زر حساب الإجمالي بتصميم حديث
        حساب_زر = ttk.Button(self.frame, text="حساب الإجمالي", command=self.حساب_الإجمالي)
        حساب_زر.pack(pady=10)
        حساب_زر.bind("<Down>", lambda event: زر_عرض_الفواتير.focus())
        حساب_زر.bind("<Up>", lambda event:self.entry_اسم_المورد.focus())

        # زر عرض الفواتير بتصميم حديث
        زر_عرض_الفواتير = ttk.Button(self.frame, text="عرض الفواتير", command=self.show_invoice_list)
        زر_عرض_الفواتير.pack(pady=10)
        زر_عرض_الفواتير.bind("<Up>", lambda event: حساب_زر.focus())

        # إعداد الجدول
        self.setup_invoice_table()


    def setup_invoice_table(self):
        global tree
        tree = ttk.Treeview(self.frame, columns=("ID", "اسم المورد", "الوزن", "الوزن الصافي", "السعر", "الهالك", "الإجمالي", "الإجمالي قبل الهالك", "الفرق", "التاريخ"), show="headings")
        
        # إعداد رؤوس الأعمدة
        tree.heading("ID", text="ID")
        tree.heading("اسم المورد", text="اسم المورد")
        tree.heading("الوزن", text="الوزن (كجم)")
        tree.heading("الوزن الصافي", text="الوزن الصافي (كجم)")
        tree.heading("السعر", text="السعر (جنيه/كجم)")
        tree.heading("الهالك", text="الهالك (كجم)")
        tree.heading("الإجمالي", text="الإجمالي (جنيه)")
        tree.heading("الإجمالي قبل الهالك", text="المدفوع (جنيه)")
        tree.heading("الفرق", text="الخسارة")
        tree.heading("التاريخ", text="التاريخ")

        # ضبط عرض الأعمدة
        tree.column("ID", width=25, anchor='center')
        tree.column("الوزن", width=100, anchor='center')
        tree.column("الوزن الصافي", width=120, anchor='center')
        tree.column("السعر", width=100, anchor='center')
        tree.column("الهالك", width=100, anchor='center')
        tree.column("اسم المورد", width=120, anchor='center')
        tree.column("الإجمالي", width=100, anchor='center')
        tree.column("الإجمالي قبل الهالك", width=150, anchor='center')
        tree.column("الفرق", width=100, anchor='center')
        tree.column("التاريخ", width=120, anchor='center')

        tree.pack(fill="both", expand=True)
        tree.bind("<Double-1>", self.open_edit_window)  # ربط النقر المزدوج بفتح نافذة التعديل
         # تغيير حجم الخط وارتفاع الصفوف
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 14, "bold"), rowheight=30)  # حجم خط أكبر وارتفاع صفوف أكبر

        

    def open_edit_window(self, event):
        selected_item = tree.selection()
        if selected_item:
            self.selected_invoice_id = tree.item(selected_item)['values'][0]
            self.show_edit_window()
    
    def show_edit_window(self):
        فاتورة_id = self.selected_invoice_id
        cursor.execute("SELECT * FROM فواتير WHERE id=?", (فاتورة_id,))
        فاتورة = cursor.fetchone()
    
        edit_window = tk.Toplevel(self.frame)
        edit_window.title("تعديل الفاتورة")
    
        # تعيين الأيقونة باستخدام مسار نسبي
        icon_path = Path(__file__).parent / "chicken.ico"  # مسار نسبي للأيقونة
        edit_window.iconbitmap(str(icon_path))
        # تعيين قياس النافذة
        edit_window.geometry("250x300")  # عرض: 400، ارتفاع: 300
    
        # Helper function for creating labels and entries
        def create_label_entry(window, text, default_value):
            tk.Label(window, text=text).pack(pady=5)
            entry = tk.Entry(window)
            entry.pack(pady=5)
            entry.insert(0, default_value)
            return entry
    
        # إدخال قيم الفاتورة
        entry_اسم_المورد = create_label_entry(edit_window, "اسم المورد:", فاتورة[1])
        entry_وزن = create_label_entry(edit_window, "الوزن (كجم):", فاتورة[2])
        entry_سعر = create_label_entry(edit_window, "السعر (جنيه/كجم):", فاتورة[4])
        entry_الهالك = create_label_entry(edit_window, "الهالك (كجم):", فاتورة[5])
    
        # زر لتحديث الفاتورة بتصميم حديث
        def update_invoice():
            try:
                اسم_المورد = entry_اسم_المورد.get()
                الوزن = float(entry_وزن.get())
                السعر = float(entry_سعر.get())
                الهالك = float(entry_الهالك.get())
    
                if الوزن < 0 or السعر < 0 or الهالك < 0:
                    raise ValueError("لا يمكن أن تكون القيم سالبة!")
    
                الوزن_الصافي = الوزن - الهالك
                الإجمالي = الوزن_الصافي * السعر
                الإجمالي_قبل_الهالك = الوزن * السعر
                الفرق = الإجمالي_قبل_الهالك - الإجمالي
    
                cursor.execute("""
                UPDATE فواتير 
                SET اسم_المورد=?, الوزن=?, الوزن_الصافي=?, السعر=?, الهالك=?, الإجمالي=?, الإجمالي_قبل_الهالك=?, الفرق=? 
                WHERE id=?
                """, (اسم_المورد, الوزن, الوزن_الصافي, السعر, الهالك, round(الإجمالي, 2), round(الإجمالي_قبل_الهالك, 2), round(الفرق, 2), فاتورة_id))
                conn.commit()
                messagebox.showinfo("تحديث", "تم تحديث الفاتورة بنجاح")
                edit_window.destroy()
                self.show_invoice_list()  # تحديث الجدول بعد التعديل
    
            except ValueError as ve:
                messagebox.showerror("خطأ في الإدخال", str(ve))
            except Exception as e:
                messagebox.showerror("خطأ", "حدث خطأ أثناء التحديث.")
    
        زر_تحديث = ttk.Button(edit_window, text="تحديث", command=update_invoice)
        زر_تحديث.pack(pady=10)

        # دالة لتغيير التركيز إلى الخانة التالية عند الضغط على Enter
        def focus_next(event):
            event.widget.tk_focusNext().focus()
            return "break"  # منع الحدث الافتراضي
       
        # ربط الحدث لكل خانة إدخال
        entry_اسم_المورد.bind("<Return>", focus_next)
        entry_وزن.bind("<Return>", focus_next)
        entry_سعر.bind("<Return>", focus_next)
        entry_الهالك.bind("<Return>", lambda e: update_invoice())
       
        # التركيز على أول خانة إدخال عند فتح النافذة
        entry_اسم_المورد.focus_set()


    def حساب_الإجمالي(self):
        try:
            اسم_المورد = self.entry_اسم_المورد.get()
            الوزن = float(self.entry_الوزن.get())
            السعر = float(self.entry_سعر.get())
            الهالك = float(self.entry_الهالك.get())
            التاريخ = self.date_entry.entry.get()  

            الوزن_الصافي = الوزن - الهالك
            الإجمالي = الوزن_الصافي * السعر
            الإجمالي_قبل_الهالك = الوزن * السعر
            الفرق = الإجمالي_قبل_الهالك - الإجمالي

            # إدراج الفاتورة في قاعدة البيانات
            cursor.execute('''
                INSERT INTO فواتير (اسم_المورد, الوزن, الوزن_الصافي, السعر, الهالك, الإجمالي, الإجمالي_قبل_الهالك, الفرق, التاريخ)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (اسم_المورد, الوزن, الوزن_الصافي, السعر, الهالك, round(الإجمالي, 2), round(الإجمالي_قبل_الهالك, 2), round(الفرق, 2), التاريخ))
            conn.commit()
            messagebox.showinfo("إدخال", "تم إدخال الفاتورة بنجاح")

            self.show_invoice_list()  # تحديث الجدول بعد الإدخال

            # إعادة تعيين الحقول بعد الإدخال
            self.entry_اسم_المورد.delete(0, tk.END)
            self.entry_الوزن.delete(0, tk.END)
            self.entry_سعر.delete(0, tk.END)
            self.entry_الهالك.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال قيم صحيحة.")
    

    def show_invoice_list(self):
        # حذف البيانات الحالية في الجدول
        for item in tree.get_children():
            tree.delete(item)
    
        # عرض جميع الفواتير
        cursor.execute("SELECT * FROM فواتير ORDER BY التاريخ DESC")  

        # تعبئة الجدول بالنتائج
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def filter_invoices_by_date(self):
        selected_date = self.date_entry.entry.get()
        # مسح محتوى الجدول
        for row in tree.get_children():
            tree.delete(row)

        # استرجاع الفواتير في التاريخ المحدد
        cursor.execute("SELECT * FROM فواتير WHERE التاريخ=?", (selected_date,))
        فواتير = cursor.fetchall()

        # ملء الجدول
        for فاتورة in فواتير:
            tree.insert("", "end", values=فاتورة)

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
            

class App:
    def __init__(self):
        # إنشاء نافذة التطبيق باستخدام Tk
        self.root = tk.Tk()  # استخدام Tk مباشرة
        self.root.title("نظام إدارة الفواتير")
        
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        # بدء نافذة تسجيل الدخول أو نافذة الفواتير
        self.start_invoice_window()

        self.root.mainloop()

    def start_invoice_window(self):
        self.invoice_window = InvoiceWindow(self.frame, self.show_main_menu)

    def show_main_menu(self):
        pass  # هنا يمكنك إضافة منطق لإظهار قائمة رئيسية أو واجهة أخرى إذا رغبت

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# تشغيل التطبيق
if __name__ == "__main__":
    app = App()