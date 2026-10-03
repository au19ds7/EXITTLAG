import tkinter as tk
from tkinter import filedialog, messagebox
import secrets, string, threading, time, os

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options as ChromeOptions
except ImportError:
    webdriver = None

SIGNUP_URL = "https://www.exitlag.com/register"

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    required = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    required += [secrets.choice(chars) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(required)
    return "".join(required)

class App:
    def __init__(self, root):
        self.root = root
        root.title("ExitLag Auto Signup")
        root.geometry("600x730")
        root.configure(bg="#0d1117")

        self.password = tk.StringVar(value=generate_password())
        self.browser = tk.StringVar(value="Chrome")
        self.browser_path = tk.StringVar()
        self.proxy = tk.StringVar()
        self.speed = tk.StringVar(value="Slow (human-like)")
        self.count = tk.IntVar(value=1)
        self.plan = tk.StringVar(value="3 days")

        tk.Label(root, text="Accounts", bg="#0d1117", fg="#8b949e",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(12, 0))
        tk.Frame(root, bg="#30363d", height=1).pack(fill="x", pady=10)

        tk.Label(root, text="EXITLAG", bg="#0d1117", fg="#00c8ff",
                 font=("Consolas", 42, "bold")).pack()
        tk.Label(root, text="» New Configuration_", bg="#0d1117",
                 fg="#00d9ff", font=("Consolas", 10)).pack(pady=(0, 14))
        tk.Frame(root, bg="#30363d", height=1).pack(fill="x")

        main = tk.Frame(root, bg="#0d1117")
        main.pack(fill="both", expand=True, padx=30, pady=14)

        self.label(main, "Browser")
        row = tk.Frame(main, bg="#0d1117"); row.pack(anchor="w", pady=5)
        for name in ("Chrome", "Brave", "Opera GX"):
            tk.Radiobutton(row, text=name, value=name, variable=self.browser,
                           bg="#0d1117", fg="#d8dee9", selectcolor="#161b22",
                           activebackground="#0d1117").pack(side="left", padx=(0, 12))

        self.label(main, "Browser executable path (optional)")
        row = tk.Frame(main, bg="#0d1117"); row.pack(fill="x", pady=(4, 12))
        tk.Entry(row, textvariable=self.browser_path, bg="#161b22", fg="white",
                 insertbackground="white", relief="flat").pack(side="left", fill="x", expand=True, ipady=9)
        tk.Button(row, text="Browse", command=self.browse, bg="#21262d",
                  fg="white", relief="flat").pack(side="left", padx=7, ipady=5)

        self.label(main, "Password")
        row = tk.Frame(main, bg="#0d1117"); row.pack(fill="x", pady=(4, 12))
        tk.Entry(row, textvariable=self.password, bg="#161b22", fg="white",
                 insertbackground="white", relief="flat").pack(side="left", fill="x", expand=True, ipady=9)
        tk.Button(row, text="Generate", command=lambda: self.password.set(generate_password()),
                  bg="#21262d", fg="white", relief="flat").pack(side="left", padx=7, ipady=5)

        self.label(main, "Proxy (optional)")
        tk.Entry(main, textvariable=self.proxy, bg="#161b22", fg="white",
                 insertbackground="white", relief="flat").pack(fill="x", ipady=9, pady=(4, 12))

        self.label(main, "Fill speed")
        row = tk.Frame(main, bg="#0d1117"); row.pack(anchor="w", pady=5)
        for name in ("Slow (human-like)", "Normal", "Fast", "Super Fast"):
            tk.Radiobutton(row, text=name, value=name, variable=self.speed,
                           bg="#0d1117", fg="#d8dee9", selectcolor="#161b22",
                           activebackground="#0d1117").pack(side="left", padx=(0, 10))

        self.label(main, "Number of accounts to open")
        tk.Spinbox(main, from_=1, to=100, textvariable=self.count, width=8,
                   bg="#161b22", fg="white", buttonbackground="#21262d",
                   relief="flat").pack(anchor="w", pady=5)

        self.label(main, "Choose plan")
        row = tk.Frame(main, bg="#0d1117"); row.pack(anchor="w", pady=5)
        for name in ("3 days", "7 days"):
            tk.Radiobutton(row, text=name, value=name, variable=self.plan,
                           bg="#0d1117", fg="#d8dee9", selectcolor="#161b22",
                           activebackground="#0d1117").pack(side="left", padx=(0, 15))

        tk.Button(root, text="▶  Start", command=self.start, bg="#0878ff",
                  fg="white", relief="flat", font=("Segoe UI", 11, "bold")
                  ).pack(fill="x", padx=30, pady=(0, 20), ipady=9)

    def label(self, parent, text):
        tk.Label(parent, text=text, bg="#0d1117", fg="#8b949e",
                 font=("Segoe UI", 10)).pack(anchor="w")

    def browse(self):
        p = filedialog.askopenfilename(filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
        if p: self.browser_path.set(p)

    def start(self):
        if webdriver is None:
            messagebox.showerror("Missing dependency", "Run: pip install -r requirements.txt")
            return
        threading.Thread(target=self.open_browser, daemon=True).start()

    def open_browser(self):
        try:
            options = ChromeOptions()
            path = os.path.expandvars(self.browser_path.get().strip())
            if path and os.path.exists(path):
                options.binary_location = path
            if self.proxy.get().strip():
                options.add_argument("--proxy-server=" + self.proxy.get().strip())

            driver = webdriver.Chrome(options=options)
            driver.get(SIGNUP_URL)
            time.sleep(3)

            field = None
            for by, selector in [
                (By.CSS_SELECTOR, 'input[type="password"]'),
                (By.NAME, "password"), (By.ID, "password")
            ]:
                try:
                    candidate = driver.find_element(by, selector)
                    if candidate.is_displayed():
                        field = candidate
                        break
                except Exception:
                    pass

            if field:
                field.click()
                field.clear()
                field.send_keys(self.password.get())
                self.root.after(0, lambda: messagebox.showinfo(
                    "Ready", "Browser opened and the generated password was entered."))
            else:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Password field not found", "The site layout may have changed."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
