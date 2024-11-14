import tkinter as tk
from tkinter import messagebox
from utils.auth import register_user

class SignupPage:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.username_entry = None
        self.password_entry = None
        self.confirm_password_entry = None
        self.role_var = None  # Added for role selection

    def show(self):
        # Clear the previous frame content
        self.clear_frame()

        # Container frame for the signup form
        container = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=2)
        container.place(relx=0.5, rely=0.5, anchor="center", width=320, height=550)  # Increased height

        # Title with increased spacing
        tk.Label(
            container, text="Signup Form", font=("Arial", 18, "bold"), bg="white"
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

        # Confirm password label
        tk.Label(
            container, text="Confirm Password", font=("Arial", 10, "bold"), bg="white"
        ).pack(pady=(10, 0), anchor="w", padx=20)

        # Confirm password field with rounded corners
        confirm_password_frame = tk.Canvas(container, width=260, height=30, bg="white", highlightthickness=0)
        confirm_password_frame.pack(pady=(5, 10))
        confirm_password_frame.create_rounded_rect(0, 0, 260, 30, radius=15, fill="#f5f5f5", outline="#0a58ca")
        self.confirm_password_entry = tk.Entry(
            container,
            font=("Arial", 12),
            show="*",
            relief=tk.FLAT,
            bg="#f5f5f5",
            highlightthickness=0,
        )
        self.confirm_password_entry.place(in_=confirm_password_frame, relx=0.5, rely=0.5, anchor="center", width=250, height=25)

        # Role selection label
        tk.Label(
            container, text="Select Role", font=("Arial", 10, "bold"), bg="white"
        ).pack(pady=(10, 0), anchor="w", padx=20)

        # Dropdown for selecting role
        self.role_var = tk.StringVar(value="User")  # Default value
        role_dropdown = tk.OptionMenu(container, self.role_var, "User", "Admin")
        role_dropdown.config(font=("Arial", 12), relief=tk.FLAT, width=18, bg="#f5f5f5")
        role_dropdown.pack(pady=(5, 15))

        # Signup button
        tk.Button(
            container,
            text="Sign Up",
            font=("Arial", 12, "bold"),
            bg="#0a58ca",
            fg="white",
            width=20,
            relief=tk.FLAT,
            command=self.attempt_signup,
        ).pack(pady=15)

        # Login link
        tk.Label(container, text="Already a member?", font=("Arial", 10), bg="white", fg="gray").pack()
        tk.Button(
            container,
            text="Login",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#0a58ca",
            relief=tk.FLAT,
            command=self.app.show_login,
        ).pack()

    def attempt_signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        role = self.role_var.get()  # Get the selected role

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Attempt to register the user with the selected role
        if register_user(username, password, role):  # Pass role to register_user
            messagebox.showinfo("Signup Success", "Your account has been created!")
            self.app.show_login()
        else:
            messagebox.showerror("Error", "Signup failed. Try a different username.")

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
