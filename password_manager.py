import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
import json
import os
from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер паролей")
        self.root.geometry("600x450")
        
        # --- Шифрование ---
        self.key_file = 'secret.key'
        self.data_file = 'passwords.json'
        self._init_crypto()
        
        # --- Vариант 2: StringVar ---
        self.site_var = tk.StringVar()
        self.login_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        
        # --- Вкладки ---
        self.tab_control = ttk.Notebook(root)
        
        self.tab_generate = ttk.Frame(self.tab_control)  # Генератор
        self.tab_store = ttk.Frame(self.tab_control)     # Хранилище
        
        self.tab_control.add(self.tab_generate, text='🔐 Генератор')
        self.tab_control.add(self.tab_store, text='🗄️ Хранилище')
        self.tab_control.pack(expand=1, fill='both')
        
        # --- Настройки вкладок ---
        self._setup_generate_tab()
        self._setup_store_tab()
        
    def _init_crypto(self):
        """Инициализация ключа шифрования"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher = Fernet(self.key)
        
    def _setup_generate_tab(self):
        """Настройка вкладки генератора"""
        frame = ttk.LabelFrame(self.tab_generate, text="Генерация пароля")
        frame.pack(pady=20, padx=20, fill='x')
        
        ttk.Label(frame, text="Длина пароля:").grid(row=0, column=0, padx=10, pady=10)
        self.length_var = tk.IntVar(value=16)
        ttk.Spinbox(frame, from_=8, to=64, textvariable=self.length_var, width=5).grid(row=0, column=1, padx=10, pady=10)
        
        # Чекбоксы
        self.upper_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(frame, text="Заглавные буквы (A-Z)", variable=self.upper_var).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        ttk.Checkbutton(frame, text="Цифры (0-9)", variable=self.digits_var).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        ttk.Checkbutton(frame, text="Символы (!@#$...)", variable=self.symbols_var).grid(row=3, column=0, padx=10, pady=5, sticky='w')
        
        # Вывод
        ttk.Label(frame, text="Пароль:").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.result_entry = ttk.Entry(frame, font=("Arial", 14, "bold"), width=40)
        self.result_entry.grid(row=4, column=1, padx=10, pady=10, columnspan=2)
        
        # Кнопки
        ttk.Button(frame, text="Генерировать", command=self.generate_password).grid(row=5, column=0, padx=10, pady=10)
        ttk.Button(frame, text="Копировать", command=self.copy_password).grid(row=5, column=1, padx=10, pady=10)
        
        # Заметка
        ttk.Label(frame, text="⚠️ Заметка: храните пароли в секрете!", foreground="red").grid(row=6, column=0, columnspan=3, pady=10)
        
    def _setup_store_tab(self):
        """Настройка вкладки хранилища"""
        # Основный фрейм
        frame = ttk.LabelFrame(self.tab_store, text="Сохраненные пароли")
        frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # --- Верхняя часть: поля ввода (используем grid) ---
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Название (сайт/сервис):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.site_entry = ttk.Entry(input_frame, textvariable=self.site_var, width=30)
        self.site_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Логин:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.login_entry = ttk.Entry(input_frame, textvariable=self.login_var, width=30)
        self.login_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Пароль (можно сгенерированный):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.pass_entry = ttk.Entry(input_frame, textvariable=self.pass_var, width=30)
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Добавить в хранилище", command=self.add_entry).grid(row=3, column=0, columnspan=2, pady=10)
        
        # --- Нижняя часть: таблица и кнопка (используем pack) ---
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(table_frame, columns=('ID', 'Сайт', 'Логин', 'Пароль'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Сайт', text='Сайт')
        self.tree.heading('Логин', text='Логин')
        self.tree.heading('Пароль', text='Пароль')
        
        self.tree.column('ID', width=40)
        self.tree.column('Сайт', width=150)
        self.tree.column('Логин', width=120)
        self.tree.column('Пароль', width=150)
        
        self.tree.pack(fill='both', expand=True)
        
        ttk.Button(table_frame, text="Удалить выбранное", command=self.delete_entry).pack(pady=5)
        
        # Обновляем таблицу
        self.refresh_table()
        
    def generate_password(self):
        """Генерация безопасного пароля"""
        length = self.length_var.get()
        if length < 8:
            messagebox.showerror("Ошибка", "Пароль должен быть не короче 8 символов!")
            return
        
        chars = string.ascii_lowercase
        if self.upper_var.get():
            chars += string.ascii_uppercase
        if self.digits_var.get():
            chars += string.digits
        if self.symbols_var.get():
            chars += string.punctuation
        
        # Используем secrets вместо random для криптографической безопасности
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, password)
        
    def copy_password(self):
        """Копирование пароля в буфер обмена"""
        password = self.result_entry.get()
        if not password:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте пароль!")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        messagebox.showinfo("Успех", "Пароль копирован в буфер обмена!")
        
    def add_entry(self):
        """Добавление записи в хранилище"""
        site = self.site_var.get().strip()
        login = self.login_var.get().strip()
        password = self.pass_var.get().strip()
        
        if not site or not login or not password:
            messagebox.showerror("Ошибка", "Введите все поля!")
            return
        
        # Читаем существующие данные
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Шифруем пароль перед сохранением
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        
        data.append({
            'id': len(data) + 1,
            'site': site,
            'login': login,
            'password': encrypted_password
        })
        
        with open(self.data_file, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
        
        # Очищаем поля (используем StringVar)
        self.site_var.set("")
        self.login_var.set("")
        self.pass_var.set("")
        
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись добавлена!")
        
    def refresh_table(self):
        """Обновляем таблицу"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            for row in data:
                # Расшифровываем пароль для отображения
                decrypted = self.cipher.decrypt(row['password'].encode()).decode()
                self.tree.insert('', 'end', values=(row['id'], row['site'], row['login'], decrypted))
        
    def delete_entry(self):
        """Удаление записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления!")
            return
        
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]
        
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            data = [entry for entry in data if entry['id'] != entry_id]
            
            with open(self.data_file, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=4))
        
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись удалена!")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()