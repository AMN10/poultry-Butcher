from pathlib import Path
import tkinter as tk
import ttkbootstrap as ttkb
import json
import os
from datetime import datetime, timedelta
from tkinter import messagebox  # لعرض رسالة التنبيه
from ttkbootstrap.widgets import DateEntry  # استيراد DateEntry
import pygame  # استيراد مكتبة pygame لتشغيل الصوت

class DebtsWindow:
    def __init__(self, parent_frame):
        self.frame = ttkb.Frame(parent_frame)
        self.frame.pack(fill="both", expand=True)
        # تهيئة edit_window إلى None
        self.edit_window = None
        self.last_alert_date = None  # متغير لتخزين آخر تاريخ تم عرض الرسالة فيه
        self.delay_duration = 2000  # مدة التأخير بالمللي ثانية (هنا 5000 مللي ثانية = 5 ثواني)

        # إعداد pygame لتشغيل الصوت
        pygame.mixer.init()

        # عنوان النافذة
        title_label = ttkb.Label(self.frame, text="إدارة المديونية", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=20)

        # خانة إدخال لاسم المدين
        name_label = ttkb.Label(self.frame, text="اسم المدين", font=("Helvetica", 12))
        name_label.pack(pady=0)

        self.debt_name_entry = ttkb.Entry(self.frame, width=15, font=("Helvetica", 12))
        self.debt_name_entry.pack(pady=5)
        # تركيز المؤشر على حقل اسم المدين عند بدء التشغيل
        self.debt_name_entry.focus()


        # خانة إدخال للمبلغ
        amount_label = ttkb.Label(self.frame, text="المبلغ", font=("Helvetica", 12))
        amount_label.pack(pady=0)

        self.debt_amount_entry = ttkb.Entry(self.frame, width=10, font=("Helvetica", 12))
        self.debt_amount_entry.pack(pady=5)
         # تحديد وظيفة التحقق
        vcmd = (self.debt_amount_entry.register(self.validate_amount), '%P')
        self.debt_amount_entry.config(validate='key', validatecommand=vcmd)

         # خانة إدخال لتاريخ السداد باستخدام DateEntry
        repayment_label = ttkb.Label(self.frame, text="تاريخ السداد", font=("Helvetica", 12))
        repayment_label.pack(pady=5)

        self.repayment_date_entry = DateEntry(self.frame)
        self.repayment_date_entry.pack(pady=10)

        # زر لإضافة الدين
        add_debt_button = ttkb.Button(
            self.frame,
            text="إضافة دين",
            command=self.add_debt,
            bootstyle="success",
            width=10
        )
        add_debt_button.pack(pady=10)
        add_debt_button.bind("<Return>", lambda e: self.add_debt())
        self.repayment_date_entry.entry.bind("<Return>", lambda e: add_debt_button.focus())



        # إنشاء Treeview لعرض الديون
        self.debt_treeview = ttkb.Treeview(self.frame, columns=( "repayment_date", "date", "amount", "name"), show='headings', height=15)
        self.debt_treeview.pack(pady=10)

        # تعريف الأعمدة مع عرض محدد
        self.debt_treeview.heading("repayment_date", text="تاريخ السداد")
        self.debt_treeview.heading("date", text="تاريخ الدين")
        self.debt_treeview.heading("amount", text="المبلغ")
        self.debt_treeview.heading("name", text="اسم المدين")

        # إنشاء Style للتعديل على شكل الجدول
        self.style = ttkb.Style()
        self.style.configure("Treeview", font=("Helvetica", 14, "bold"), rowheight=35)  # حجم خط أكبر وارتفاع صفوف أكبر

        # عرض الأعمدة
        self.debt_treeview.column("repayment_date", width=200, anchor='center')  # عمود تاريخ السداد
        self.debt_treeview.column("date", width=200, anchor='center')  # عمود التاريخ
        self.debt_treeview.column("amount", width=200, anchor='center')  # عمود المبلغ
        self.debt_treeview.column("name", width=200, anchor='center')  # عمود اسم المدين

         # ربط حدث الضغط المزدوج على الصف
        self.debt_treeview.bind("<Double-1>", self.on_double_click)
        self.debt_treeview.bind("<Return>", self.on_double_click)
        

        # اسم ملف JSON
        self.json_file = 'debts.json'
        # تحميل الديون الموجودة عند بدء التطبيق
        self.load_debts()

        # التحقق اليومي من تواريخ السداد
        self.check_due_dates()

        # ربط المفاتيح لتنقل باستخدام Enter
        self.bind_events()

        # تركيز المؤشر على حقل اسم المدين عند بدء التشغيل
        self.debt_name_entry.focus()

    def validate_amount(self, new_value):
        """التأكد من أن الإدخال في حقل المبلغ يتضمن أرقاماً فقط أو أرقام عشرية."""
        if new_value == "":
            return True  # السماح بأن تكون الخانة فارغة مؤقتًا
        try:
            float(new_value)  # محاولة تحويل القيمة إلى رقم حقيقي (float)
            return True
        except ValueError:
            return False  # منع أي إدخال غير رقمي أو غير عشري

    def bind_events(self):
        """ربط أزرار Enter للتنقل بين الحقول."""
        self.debt_name_entry.bind("<Return>", lambda e: self.debt_amount_entry.focus())
        self.debt_amount_entry.bind("<Return>", lambda e: self.repayment_date_entry.entry.focus())


    def load_debts(self):
        """تحميل الديون من ملف JSON إذا كان موجودًا."""
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as file:
                debts = json.load(file)
                for debt in debts:
                    self.debt_treeview.insert("", tk.END, values=(debt.get('repayment_date', '---'), debt['date'], debt['amount'], debt['name']))

    def add_debt(self):
        """إضافة دين جديد بعد التحقق من أن الحقول ليست فارغة."""
        debt_name = self.debt_name_entry.get()
        debt_amount = self.debt_amount_entry.get()
        repayment_date = self.repayment_date_entry.entry.get()

        if not debt_name:  # التحقق من أن حقل اسم المدين ليس فارغًا
            messagebox.showwarning("تنبيه", "يرجى إدخال اسم المدين.")
            return

        if not debt_amount:  # التحقق من أن حقل المبلغ ليس فارغًا
            messagebox.showwarning("تنبيه", "يرجى إدخال المبلغ.")
            return

        debt_name = self.debt_name_entry.get()
        debt_amount = self.debt_amount_entry.get()
        repayment_date = self.repayment_date_entry.entry.get()

        if debt_name and debt_amount:  # التأكد من أن الحقول ليست فارغة
            # الحصول على التاريخ الحالي
            current_date = datetime.now().strftime("%Y-%m-%d")

            # إضافة الدين إلى Treeview (correct column order)
            self.debt_treeview.insert("", tk.END, values=(repayment_date, current_date, debt_amount, debt_name))

            # حفظ الدين في ملف JSON
            self.save_debt(debt_name, debt_amount, current_date, repayment_date)

            # مسح حقول الإدخال (reset to current date)
            self.debt_name_entry.delete(0, tk.END)
            self.debt_amount_entry.delete(0, tk.END)
            self.repayment_date_entry.entry.delete(0, tk.END)
            self.repayment_date_entry.entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def save_debt(self, name, amount, date, repayment_date):
        """حفظ الدين في ملف JSON."""
        debt = {'name': name, 'amount': amount, 'date': date, 'repayment_date': repayment_date}

        # تحميل البيانات الموجودة
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as file:
                debts = json.load(file)
        else:
            debts = []

        # إضافة الدين الجديد
        debts.append(debt)

        # حفظ البيانات في الملف JSON
        with open(self.json_file, 'w', encoding='utf-8') as file:
            json.dump(debts, file, ensure_ascii=False, indent=4)

           # التحقق اليومي من تواريخ السداد
        self.check_due_dates()

    def check_due_dates(self):
        """التحقق من تواريخ السداد وتنبيه المستخدم."""
        today = datetime.now().strftime("%Y-%m-%d")
        debts_due_today = []

        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as file:
                debts = json.load(file)

                for debt in debts:
                    if debt['repayment_date'] == today:
                        debts_due_today.append(debt)

        if debts_due_today:
            # تحقق مما إذا كانت الرسالة قد عرضت بالفعل اليوم
            if self.last_alert_date != today:
                # تأخير عرض الرسالة
                self.frame.after(self.delay_duration, lambda: self.show_due_messages(debts_due_today))
                self.last_alert_date = today  # تحديث آخر تاريخ عرض الرسالة

        # قم بالتحقق مرة أخرى بعد 24 ساعة
        self.frame.after(86400000, self.check_due_dates)  # 86400000 ميلي ثانية = 24 ساعة

    def show_due_messages(self, debts_due_today):
        """عرض الرسائل الخاصة بالديون المستحقة."""
        for debt in debts_due_today:
            self.play_alert_sound()  # تشغيل الصوت المخصص
            messagebox.showwarning(
                "تنبيه تاريخ السداد",
                f"اليوم هو تاريخ السداد للمدين {debt['name']} بمبلغ {debt['amount']}."
            )
    def play_alert_sound(self):
        """تشغيل صوت التنبيه."""
      # الحصول على المسار الحالي للملف
        base_path = Path(__file__).parent
        sound_file = base_path / "cook.wav"  # مسار الملف الصوتي النسبي
    
        if sound_file.exists():
            pygame.mixer.music.load(str(sound_file))  # تحويل المسار إلى نص لاستخدامه في pygame
            pygame.mixer.music.play()
        else:
            print("ملف الصوت غير موجود!")

    
    def on_double_click(self, event):
        """فتح نافذة التعديل عند الضغط مرتين على أحد الأسطر."""
        item = self.debt_treeview.selection()[0]  # الحصول على العنصر المحدد
        debt_data = self.debt_treeview.item(item, 'values')

        if self.edit_window is not None and tk.Toplevel.winfo_exists(self.edit_window):
            return self.edit_window.attributes('-topmost', True)  # اجعل النافذة في المقدمة # إذا كانت نافذة التعديل مفتوحة بالفعل، لا تقم بفتح نافذة أخرى


        # إنشاء نافذة تعديل
        self.edit_window = tk.Toplevel(self.frame)
        self.edit_window.title("تعديل الدين")
        self.edit_window.geometry("260x350")

        # استخدام المسار النسبي للأيقونة
        base_path = Path(__file__).parent
        icon_path = base_path / "chicken.ico"
        if icon_path.exists():
            self.edit_window.iconbitmap(icon_path)
        else:
            print("Icon file not found")


        # عرض البيانات الحالية في حقول الإدخال
        edit_name_label = ttkb.Label(self.edit_window, text="اسم المدين", font=("Helvetica", 10))
        edit_name_label.pack(pady=0)

        edit_name_entry = ttkb.Entry(self.edit_window, width=15, font=("Helvetica", 12))
        edit_name_entry.pack(pady=8)
        edit_name_entry.insert(0, debt_data[3])  # اسم المدين
         # تركيز المؤشر على حقل اسم المدين عند بدء التشغيل
        edit_name_entry.focus()
         # إضافة حدث للانتقال للحقل التالي
        edit_name_entry.bind("<Return>", lambda event: edit_amount_entry.focus_set())

        

        edit_amount_label = ttkb.Label(self.edit_window, text="المبلغ", font=("Helvetica", 10))
        edit_amount_label.pack(pady=0)

        edit_amount_entry = ttkb.Entry(self.edit_window, width=10, font=("Helvetica", 12))
        edit_amount_entry.pack(pady=8)
        edit_amount_entry.insert(0, debt_data[2])  # المبلغ
        # إضافة حدث للانتقال للحقل التالي
        edit_amount_entry.bind("<Return>", lambda event: edit_date_entry.focus_set())


        edit_date_label = ttkb.Label(self.edit_window, text="تاريخ السداد", font=("Helvetica", 10))
        edit_date_label.pack(pady=0)

        edit_date_entry = DateEntry(self.edit_window, width=10)
        edit_date_entry.pack(pady=8)
        edit_date_entry.entry.insert(0, debt_data[0])  # تاريخ السداد
        # إضافة حدث عند الضغط على إنتر في حقل التاريخ
        edit_date_entry.entry.bind("<Return>", lambda event: save_button.invoke())  # استدعاء زر الحفظ


        # زر حفظ التعديلات
        save_button = ttkb.Button(
            self.edit_window,
            text="حفظ التعديلات",
             bootstyle="primary",
            command=lambda: self.save_edits(item, edit_name_entry.get(), edit_amount_entry.get(), edit_date_entry.entry.get())
            )
        save_button.pack(pady=10)

        # زر حذف الدين
        delete_button = ttkb.Button(
            self.edit_window,
            text="حذف الدين",
            bootstyle="danger",
            command=lambda: self.delete_debt(item)
        )
        delete_button.pack(pady=10)

    def save_edits(self, item, new_name, new_amount, new_date):
        """حفظ التعديلات المدخلة على الدين."""
        self.debt_treeview.item(item, values=(new_date, self.debt_treeview.item(item, 'values')[1], new_amount, new_name))
        self.update_json()

        if self.edit_window:
            self.edit_window.destroy()
            

    def on_delete_key(self, event):
        """التحقق من وجود صف محدد وحذفه عند الضغط على زر Delete."""
        selected_item = self.debt_treeview.selection()
        if selected_item:  # إذا كان هناك صف محدد
            self.delete_debt(selected_item[0])  # حذف الصف المحدد


    def delete_debt(self, item):
        
        """حذف الدين المحدد."""
        confirmation = messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا الدين؟")
        if confirmation:
            try:
                self.debt_treeview.delete(item)  # محاولة حذف العنصر
                self.update_json()  # تحديث ملف JSON بعد الحذف
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء محاولة حذف الدين: {str(e)}")

        if self.edit_window:
            self.edit_window.destroy()

    def update_json(self):
        """تحديث ملف JSON بعد التعديل أو الحذف."""
        debts = []
        for row in self.debt_treeview.get_children():
            debt_values = self.debt_treeview.item(row, 'values')
            debt = {
                'repayment_date': debt_values[0],
                'date': debt_values[1],
                'amount': debt_values[2],
                'name': debt_values[3]
            }
            debts.append(debt)

        with open(self.json_file, 'w', encoding='utf-8') as file:
            json.dump(debts, file, ensure_ascii=False, indent=4)


# لإنشاء نافذة رئيسية لتجربة التطبيق
if __name__ == "__main__":
    root = ttkb.Window(themename="darkly")  # إنشاء نافذة جديدة
    debts_window = DebtsWindow(root)
    root.mainloop()
