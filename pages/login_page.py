import tkinter as tk
from tkinter import messagebox
from utils.auth import login_user, save_remember_me, get_remember_me, clear_remember_me


class LoginPage:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.remember_me_var = tk.BooleanVar()
        self.username_entry = None
        self.password_entry = None

    def show(self):
        # Clear the previous frame content
        self.clear_frame()

        # Container frame for the login form
        container = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=2)
        container.place(relx=0.5, rely=0.5, anchor="center", width=320, height=450)

        # Title with increased spacing
        tk.Label(
            container, text="Login Form", font=("Arial", 18, "bold"), bg="white"
        ).pack(pady=(20, 20))  # Added more y-spacing

        # Username label
        tk.Label(
            container, text="Username", font=("Arial", 10, "bold"), bg="white"
        ).pack(pady=(10, 0), anchor="w", padx=20)

        # Username field with rounded corners
        username_frame = tk.Canvas(container, width=260, height=30, bg="white", highlightthickness=0)
        username_frame.pack(pady=(5, 10))
        username_frame.create_rounded_rect(0, 0, 260, 30, radius=15, fill="#f5f5f5", outline="#0a58ca")
        self.username_entry = tk.Entry(
            container,
            font=("Arial", 12),
            relief=tk.FLAT,
            bg="#f5f5f5",
            highlightthickness=0,
        )
        self.username_entry.place(in_=username_frame, relx=0.5, rely=0.5, anchor="center", width=250, height=25)

        # Password label
        tk.Label(
            container, text="Password", font=("Arial", 10, "bold"), bg="white"
        ).pack(pady=(10, 0), anchor="w", padx=20)

        # Password field with rounded corners
        password_frame = tk.Canvas(container, width=260, height=30, bg="white", highlightthickness=0)
        password_frame.pack(pady=(5, 10))
        password_frame.create_rounded_rect(0, 0, 260, 30, radius=15, fill="#f5f5f5", outline="#0a58ca")
        self.password_entry = tk.Entry(
            container,
            font=("Arial", 12),
            show="*",
            relief=tk.FLAT,
            bg="#f5f5f5",
            highlightthickness=0,
        )
        self.password_entry.place(in_=password_frame, relx=0.5, rely=0.5, anchor="center", width=250, height=25)

        # Display any remembered username
        remembered_username = get_remember_me()
        if remembered_username:
            self.username_entry.insert(0, remembered_username)
            self.remember_me_var.set(True)

        # "Remember Me" checkbox
        tk.Checkbutton(
            container,
            text="Remember Me",
            variable=self.remember_me_var,
            bg="white",
            fg="gray",
            font=("Arial", 10),
            relief=tk.FLAT,
        ).pack(pady=(10, 0))

        # Login button
        tk.Button(
            container,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#0a58ca",
            fg="white",
            width=20,
            relief=tk.FLAT,
            command=self.attempt_login,
        ).pack(pady=15)

        # Signup link
        tk.Label(container, text="Not a member?", font=("Arial", 10), bg="white", fg="gray").pack()
        tk.Button(
            container,
            text="Sign Up",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#0a58ca",
            relief=tk.FLAT,
            command=self.app.show_signup,
        ).pack()

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = login_user(username, password)
        if user:
            messagebox.showinfo("Login Success", "Welcome!")

            if self.remember_me_var.get():
                save_remember_me(username)
            else:
                clear_remember_me()

            # Navigate to the appropriate dashboard
            if user["role"] == "admin":
                self.app.show_admin_dashboard(username)
            else:
                self.app.show_user_dashboard(username)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def clear_frame(self):
        """Utility function to clear all widgets from the root frame."""
        for widget in self.root.winfo_children():
            widget.destroy()


# Adding the `create_rounded_rect` function for `Canvas`
def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius,
        y1,
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


tk.Canvas.create_rounded_rect = create_rounded_rect
