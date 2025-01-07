from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry
from reports import ReportsWindow  # استدعاء ملف التقارير
from ttkbootstrap import Style  # استدعاء المكتبة لاستخدام السمات الحديثة
from ttkbootstrap.widgets import DateEntry

# الاتصال بقاعدة البيانات
db_path = Path.home() / "المبيعات.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to initialize the database
def initialize_database():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS المصنفات (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            الاسم TEXT UNIQUE NOT NULL
        )
    """)
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

initialize_database()  # Ensure this is called

# الأصناف الأساسية
الأصناف_الأساسية = [
    "شاورما", "شيش", "فراخ صندوق (شوايه)", "اجنحه", 
    "صدور مخليه (بانيه)", "كبد وقوانص", "كوردن بلو", 
    "استربس", "شيش طاووق", "حمام كداب", 
    "هياكل (جناح ورقبه)", "هياكل عضم", "فراخ زبون", "قطاعي"
]

for صنف in الأصناف_الأساسية:
    try:
        cursor.execute("INSERT INTO المصنفات (الاسم) VALUES (?)", (صنف,))
    except sqlite3.IntegrityError:
        pass
conn.commit()

class SalesWindow:
    def __init__(self, frame, return_to_main):
        self.frame = frame
        self.return_to_main = return_to_main
        # قم بتحميل المصنفات هنا
        self.المصنفات = self.load_categories()  # تأكد من تحميل المصنفات
        self.selected_category = tk.StringVar(value=None)  # تعيين القيمة الافتراضية إلى None
        self.title_font = ("Helvetica", 14, "bold")

        self.edit_window_open = False  # متغير لتتبع حالة نافذة التعديل
        
        self.show_sales_window()

    def load_categories(self):
        cursor.execute("SELECT الاسم FROM المصنفات")
        return [row[0] for row in cursor.fetchall()]

    def show_sales_window(self):

        
        self.clear_frame()  # حذف محتويات الإطار
        tk.Label(self.frame, text="المبيعات", font=("Helvetica", 25)).pack(pady=0)
    
        # إطار لتقسيم النافذة
        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # إعداد الإطارات
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=0, pady=0)
    
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)  # توسع إلى كامل المساحة
    
        # زر عرض الكل في أعلى الجدول
        زر_عرض_الكل = ttk.Button(left_frame, text="عرض الكل", command=self.show_all_sales, width=20)
        زر_عرض_الكل.pack(pady=(10, 5))
        
        # إعداد الجدول
        self.columns = ("المصنف", "الوزن", "السعر", "الإجمالي", "التاريخ", "الوقت")
        self.tree = ttk.Treeview(left_frame, columns=self.columns, show="headings", height=10)
    
        # إضافة شريط تمرير عمودي
        self.scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
    
        # إضافة شريط التمرير
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
    
        # وضع الجدول في منتصف الإطار الأيسر
        self.tree.pack(expand=True, fill="both", pady=(0, 0))
    
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=170, anchor="center")  # زيادة عرض الأعمدة
    
        # إطار الأزرار والخانات (النصف الأيمن)
        right_inner_frame = tk.Frame(right_frame)
        right_inner_frame.pack(pady=0, fill=tk.BOTH, expand=True)
    
        self.date_entry = DateEntry(right_inner_frame, bootstyle="success")
        self.date_entry.pack(pady=(50, 5))
        self.date_entry.bind("<<DateEntrySelected>>", lambda e: self.update_sales_table())

        # إضافة زر فلترة حسب التاريخ المختار
        زر_فلترة_حسب_التاريخ = ttk.Button(right_inner_frame, text="فلترة ", command=self.filter_by_date, width=8)
        زر_فلترة_حسب_التاريخ.pack(pady=(5, 50))

        زر_فلترة_حسب_التاريخ.bind("<Up>", lambda e:زر_عرض_الكل.focus_set())
        زر_عرض_الكل.bind("<Down>", lambda e: زر_فلترة_حسب_التاريخ.focus_set())

    
        # إنشاء قائمة منسدلة لاختيار المصنف
        self.selected_category = tk.StringVar(value=None)  # تعيين القيمة الافتراضية إلى None
        self.option_menu = ttk.OptionMenu(right_inner_frame, self.selected_category, 'اختر مصنف', *self.المصنفات, command=self.update_sales_table)
        self.option_menu.pack(pady=5)
        # اجعل القائمة المنسدلة تستقبل التركيز
        self.option_menu.focus_set()
        
        # إطار للوزن والسعر
        weight_price_frame = tk.Frame(right_inner_frame)
        weight_price_frame.pack(pady=10)
    
        # وزن
        tk.Label(weight_price_frame, text=":الوزن (كجم)", font=("Helvetica", 12)).grid(row=0, column=1, padx=5, pady=5)
        self.entry_السعر = tk.Entry(weight_price_frame, width=8, font=("Helvetica", 14))
        self.entry_السعر.grid(row=1, column=0, padx=5, pady=5)
    
        # سعر 
        tk.Label(weight_price_frame, text=":السعر (جنيه)", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.entry_الوزن = tk.Entry(weight_price_frame, width=8, font=("Helvetica", 14))
        self.entry_الوزن.grid(row=1, column=1, padx=5, pady=5)
                # الانتقال من خانة الوزن إلى خانة السعر عند الضغط على السهم الأيمن
        self.entry_الوزن.bind("<KeyPress-Left>", lambda e: self.entry_السعر.focus_set())
        
        # الانتقال من خانة السعر إلى خانة الوزن عند الضغط على السهم الأيسر
        self.entry_السعر.bind("<KeyPress-Right>", lambda e: self.entry_الوزن.focus_set())
    
        # الانتقال إلى خانة السعر عند الضغط على Enter في خانة الوزن
        self.entry_الوزن.bind("<Return>", lambda e: self.entry_السعر.focus_set())
    
        حساب_زر = ttk.Button(weight_price_frame, text="إضافة", command=self.حساب_الإجمالي, width=10, padding=(10, 5))  # تكبير الزر
        حساب_زر.grid(row=2, columnspan=2, pady=10)

         # الانتقال إلى زر الفلترة عند الضغط على السهم لأعلى
        زر_فلترة_حسب_التاريخ.bind("<Down>", lambda e: self.option_menu.focus_set())
        # الانتقال إلى قائمة "اختر مصنف" عند الضغط على السهم لأعلى
        self.option_menu.bind("<Up>", lambda e: زر_فلترة_حسب_التاريخ.focus_set())

        # الانتقال باستخدام الأسهم
        self.entry_الوزن.bind("<Up>", lambda e: self.option_menu.focus_set())  # الانتقال إلى خانة السعر عند الضغط على السهم لأسفل
        self.option_menu.bind("<Down>", lambda e:self.entry_الوزن.focus_set())
        self.entry_الوزن.bind("<Down>", lambda e:حساب_زر.focus_set())  # الانتقال إلى السعر عند الضغط على سهم للأسفل
        حساب_زر.bind("<Up>", lambda e: self.entry_الوزن.focus_set())  # العودة إلى الوزن عند الضغط على سهم للأعلى
        self.entry_السعر.bind("<Down>", lambda e: حساب_زر.focus_set())  # الانتقال إلى زر الإضافة عند الضغط على سهم للأسفل
        
       
    
        # الضغط على زر "إضافة" بعد إدخال السعر والضغط على Enter
        self.entry_السعر.bind("<Return>", lambda e: حساب_زر.invoke())
    
        buttons_frame = tk.Frame(right_inner_frame)
        buttons_frame.pack(pady=20)
    
        # زر التقارير أسفل الجدول
        زر_التقارير = ttk.Button(right_inner_frame, text="التقارير الشهرية والسنوية", command=self.open_reports_window, width=25, padding=(10, 10))
        زر_التقارير.pack(pady=10)
    
        حساب_زر.bind("<Down>", lambda e: زر_التقارير.focus_set())
        زر_التقارير.bind("<Up>", lambda e: حساب_زر.focus_set())
       

       
    
        self.tree.bind("<Double-1>", self.edit_sale)
    
        # إضافة حدث الضغط على Enter لفتح نافذة التعديل
        def edit_sale_on_enter(event):
            selected_item = self.tree.selection()
            if selected_item:
                self.edit_sale(None)  # تمرير None للمسار لاستخدام الحدث الحالي
    
        self.tree.bind("<Return>", edit_sale_on_enter)
    
        # تغيير حجم الخط في الجدول
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 11))  # حجم خط الجدول
    
        # تحديد الوزن لتوسيع الجدول
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
    
        # ضبط حجم الإطارات
        right_inner_frame.grid_rowconfigure(0, weight=1)  # وزن الصف الأول
        right_inner_frame.grid_columnconfigure(0, weight=1)  # وزن العمود الأول
        
        # تغيير حجم الخط وارتفاع الصفوف
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 14, "bold"), rowheight=30)  # حجم خط أكبر وارتفاع صفوف أكبر

        self.update_sales_table()  # تحديث الجدول عند البدء
        self.show_totals_for_all_categories()
    
        # متغير لتتبع التركيز بين الجدول وخانة "اختر الصنف"
        self.is_table_focused = False

    def show_popdown_menu(self):
        # إنشاء قائمة منسدلة
        menu = tk.Menu(self.frame, tearoff=0)
        for category in self.المصنفات:
            menu.add_command(label=category, command=lambda c=category: self.select_category(c))
         # إظهار القائمة المنسدلة عند الزر
        menu.post(self.frame.winfo_pointerx(), self.frame.winfo_pointery())
    
    def select_category(self, category):
        # تعبئة خانة الإدخال بالقيمة المختارة
        self.entry_المصنف.delete(0, tk.END)
        self.entry_المصنف.insert(0, category)
        self.update_sales_table()

    
    def load_categories(self):
        cursor.execute("SELECT الاسم FROM المصنفات")
        return [row[0] for row in cursor.fetchall()]

    def حساب_الإجمالي(self):
        try:
            المصنف_مختار = self.selected_category.get()
            if not المصنف_مختار:
                raise ValueError("الرجاء اختيار مصنف")

            الوزن = float(self.entry_الوزن.get())
            السعر = float(self.entry_السعر.get())
            الإجمالي = الوزن * السعر
            التاريخ = self.date_entry.entry.get()
            الوقت = datetime.now().strftime("%H:%M:%S")
            # إضافة البيانات إلى قاعدة البيانات
            cursor.execute("INSERT INTO مبيعات (المصنف, الوزن, السعر, الإجمالي, التاريخ, الوقت) VALUES (?, ?, ?, ?, ?, ?) ",
                           (المصنف_مختار, الوزن, السعر, الإجمالي, التاريخ, الوقت))
            conn.commit()
             # إظهار رسالة بالنجاح
            messagebox.showinfo("الإجمالي", f"الإجمالي هو: {الإجمالي:.2f} جنيه")
             # تفريغ الخانات بعد الإضافة
            self.entry_الوزن.delete(0, tk.END)
            self.entry_السعر.delete(0, tk.END)
            self.selected_category.set("اختر مصنف")  # تفريغ خانة المصنف

            # تحديث الجدول
            self.update_sales_table()
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال قيم صحيحة")

    def filter_by_date(self):
        # تفريغ خانة المصنف فقط عند فلترة حسب التاريخ
        self.selected_category.set("اختر مصنف")  # تفريغ المصنف
        self.update_sales_table()

    def update_sales_table(self, *args):
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        selected_category = self.selected_category.get()
        selected_date = self.date_entry.entry.get()  # تأكد من الحصول على التاريخ بشكل صحيح
        
        if selected_category == "اختر مصنف":  # إذا كانت القيمة "اختر مصنف"
            cursor.execute("SELECT * FROM مبيعات WHERE التاريخ = ? ORDER BY التاريخ DESC, الوقت DESC", (selected_date,))
        else:  # إذا كانت خانة المصنف تحتوي على قيمة أخرى
            cursor.execute("SELECT * FROM مبيعات WHERE المصنف LIKE ? AND التاريخ = ? ORDER BY الوقت DESC", 
                       ('%' + selected_category + '%', selected_date))  # استخدام LIKE للفلترة

        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row[1:])  # استبعاد id

        # حساب المجموعات
        cursor.execute("SELECT SUM(الوزن), SUM(الإجمالي) FROM مبيعات WHERE المصنف LIKE ? AND التاريخ = ?", 
                       ('%' + selected_category + '%', selected_date))
        totals = cursor.fetchone()

        cursor.execute("SELECT SUM(الوزن), SUM(الإجمالي) FROM مبيعات WHERE المصنف = ? AND التاريخ = ?", 
                       (selected_category, selected_date))
        totals = cursor.fetchone()
        
        if totals:
            مجموع_الوزن, مجموع_الإجمالي = totals[0] or 0, totals[1] or 0
            self.show_totals_for_category(مجموع_الوزن, مجموع_الإجمالي)
        
        self.show_totals_for_all_categories()
        

    def show_totals_for_category(self, مجموع_الوزن, مجموع_الإجمالي):
        if hasattr(self, 'label_totals'):
            self.label_totals.destroy()
        self.label_totals = tk.Label(self.frame, 
                                      text=f"مجموع الوزن: {مجموع_الوزن:.2f} كجم, إجمالي السعر: {مجموع_الإجمالي:.2f} جنيه", 
                                      font=("Helvetica", 12, "bold"))
        self.label_totals.pack(pady=10)

    def show_totals_for_all_categories(self):
         selected_date = self.date_entry.entry.get()
         cursor.execute("SELECT SUM(الوزن), SUM(الإجمالي) FROM مبيعات WHERE التاريخ = ?", (selected_date,))
         totals = cursor.fetchone()
         مجموع_الوزن, مجموع_الإجمالي = totals[0] or 0, totals[1] or 0

         if hasattr(self, 'label_totals_all'):
              self.label_totals_all.destroy()

         self.label_totals_all = tk.Label(self.frame, 
                                      text=f"مجموع الوزن (لكل المصنفات لليوم): {مجموع_الوزن:.2f} كجم | مجموع الإجمالي: {مجموع_الإجمالي:.2f} جنيه", 
                                      font=("Helvetica", 12, "bold"))
         self.label_totals_all.pack(pady=5)
         
    def show_all_sales(self):
        # تفريغ خانة المصنف
        self.selected_category.set("اختر مصنف")  # تفريغ المصنف
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor.execute("SELECT * FROM مبيعات ORDER BY التاريخ DESC, الوقت DESC")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row[1:])  # استبعاد id
        self.show_totals_for_category(0, 0)
        self.show_totals_for_all_categories()

    def edit_sale(self, event):
        # التحقق مما إذا كانت هناك أي سجلات محددة
        selected_items = self.tree.selection()
        if not selected_items:  # إذا كانت قائمة العناصر المحددة فارغة
            messagebox.showwarning("تحذير", "يرجى تحديد صف أولاً لتعديله.")
            return
        
        # الحصول على السجل المحدد
        selected_item = selected_items[0]
        selected_values = self.tree.item(selected_item, "values")
        
        # استخراج القيم
        المصنف_الحالي = selected_values[0]
        الوزن_الحالي = selected_values[1]
        السعر_الحالي = selected_values[2]
        
        # التحقق مما إذا كانت نافذة تعديل موجودة بالفعل
        if hasattr(self, 'edit_window') and self.edit_window.winfo_exists():
            # إذا كانت النافذة مفتوحة بالفعل، جلبها إلى المقدمة وتركيز العمل عليها
            self.edit_window.focus_force()
            return
    
        # إنشاء نافذة منبثقة لتحرير السجل
        self.edit_window = tk.Toplevel(self.frame)
        self.edit_window.title("تحرير المبيعات")
        self.edit_window.geometry("160x260")
         # تعيين الأيقونة
        # استخدام المسار النسبي للأيقونة
        base_path = Path(__file__).parent
        icon_path = base_path / "chicken.ico"
        if icon_path.exists():
            self.edit_window.iconbitmap(icon_path)
        else:
            print("Icon file not found")


    
        # جعل النافذة فوق جميع النوافذ الأخرى والتركيز عليها
        self.edit_window.transient(self.frame)
        self.edit_window.grab_set()
        self.edit_window.focus_force()
    
         # المصنف
        tk.Label(self.edit_window, text="المصنف").pack(pady=5)
        self.selected_category_edit = tk.StringVar(value=المصنف_الحالي)  # استخدام StringVar
        self.option_menu = ttk.OptionMenu(self.edit_window, self.selected_category_edit, المصنف_الحالي, *self.المصنفات)
        self.option_menu.pack(pady=5)
        self.option_menu.focus_set()  # تركيز المؤشر على المصنف عند فتح النافذة
        
        # الوزن
        tk.Label(self.edit_window, text="الوزن").pack(pady=5)
        الوزن_entry = tk.Entry(self.edit_window, font=("Helvetica", 14), width=6)
        الوزن_entry.insert(0, الوزن_الحالي)
        الوزن_entry.pack(pady=5)
    
        # السعر
        tk.Label(self.edit_window, text="السعر").pack(pady=5)
        السعر_entry = tk.Entry(self.edit_window, font=("Helvetica", 14), width=6)
        السعر_entry.insert(0, السعر_الحالي)
        السعر_entry.pack(pady=5)
    
        # تعريف دالة حفظ التعديلات
        def save_edits():
            المصنف_الجديد = self.selected_category_edit.get()  # استخدم المتغير من OptionMenu
            الوزن_الجديد = الوزن_entry.get()
            السعر_الجديد = السعر_entry.get()
        
            # تحقق من أن الحقول ليست فارغة
            if not المصنف_الجديد or المصنف_الجديد.isdigit() or not الوزن_الجديد or not السعر_الجديد:
                messagebox.showwarning("تحذير", "يرجى ملء جميع الحقول بقيم صحيحة.")
                return
        
            try:
                # تحويل المدخلات إلى أرقام
                الوزن_الجديد_float = float(الوزن_الجديد)
                السعر_الجديد_float = float(السعر_الجديد)
                الإجمالي_الجديد = الوزن_الجديد_float * السعر_الجديد_float
            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال قيم صحيحة للأرقام.")
                return
        
            # تحديث السجل في قاعدة البيانات
            cursor.execute("""
                UPDATE مبيعات 
                SET المصنف=?, الوزن=?, السعر=?, الإجمالي=?
                WHERE المصنف=? AND الوزن=? AND السعر=?
            """, (المصنف_الجديد, الوزن_الجديد, السعر_الجديد, الإجمالي_الجديد, المصنف_الحالي, الوزن_الحالي, السعر_الحالي))
            conn.commit()
            
            # تحديث الجدول
            self.update_sales_table()
            self.edit_window.destroy()
            del self.edit_window  # حذف مرجع النافذة بعد إغلاقها
            messagebox.showinfo("تم", "تم تعديل السجل بنجاح")
        
        # دالة للانتقال بين الخانات باستخدام مفاتيح الأسهم
        def navigate(event):
            if event.keysym == 'Down':
                if الوزن_entry.focus_get() == self.option_menu:
                    الوزن_entry.focus_set()
                elif السعر_entry.focus_get() == الوزن_entry:
                    السعر_entry.focus_set()
            elif event.keysym == 'Up':
                if السعر_entry.focus_get() == الوزن_entry:
                    self.option_menu.focus_set()
                elif الوزن_entry.focus_get() == السعر_entry:
                    الوزن_entry.focus_set()
        # دالة لإغلاق النافذة عند الضغط على مفتاح "Esc"
        def close_window(event):
            cancel_edits()
    
         # ربط الأحداث
        self.option_menu.bind("<Return>", lambda e: الوزن_entry.focus_set())  # الانتقال إلى خانة الوزن
        الوزن_entry.bind("<Return>", lambda e: السعر_entry.focus_set())   # الانتقال إلى خانة السعر
        السعر_entry.bind("<Return>", lambda e: save_edits())  # حفظ التغييرات عند الضغط على Enter
        self.edit_window.bind("<Key>", navigate)  # ربط التنقل مع الأسهم
        self.edit_window.bind("<Escape>", close_window)  # إغلاق النافذة عند الضغط على Escape

        tk.Button(self.edit_window, text="حفظ", command=save_edits, font=("Helvetica", 14)).pack(pady=10)
    
        def cancel_edits():
            self.edit_window.destroy()
            del self.edit_window  # حذف مرجع النافذة بعد إغلاقها
    
        tk.Button(self.edit_window, text="إلغاء", command=cancel_edits, font=("Helvetica", 14)).pack(pady=5)


    def on_edit_window_close(self, edit_window):
        self.edit_window_open = False  # إعادة تعيين الحالة إلى مغلقة
        edit_window.destroy()  # تدمير النافذة

    def open_reports_window(self):
        ReportsWindow(self.frame, self.show_sales_window)  # تمرير الدالة لإعادة عرض نافذة المبيعات

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
            
    # تأكد من إغلاق الاتصال عند الانتهاء
    def close_database():
     conn.close()

# لا تنسَ إضافة ملف قاعدة البيانات المناسب مع الجداول المطلوبة


# الكود الخاص بتشغيل التطبيق
if __name__ == "__main__":
    root = tk.Tk()
    root.title("برنامج المبيعات")
    root.geometry("1290x650")

    # إنشاء إطار رئيسي
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    sales_window = SalesWindow(main_frame, root.quit)

    root.mainloop()

# تأكد من إغلاق الاتصال عند الانتهاء
def close_database():
    conn.close()

# لا تنسَ إضافة ملف قاعدة البيانات المناسب مع الجداول المطلوبة
