import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.filedialog import asksaveasfilename
from database.db import users_collection
import os
from PIL import Image, ImageTk  # Import Pillow for image processing
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime


class AdminDashboardPage:
    def __init__(self, root, app, username):
        self.root = root
        self.app = app
        self.username = username  # Admin username
        self.graph_size = (200, 100)  # Resize graph images for display

    def show(self):
        self.clear_frame()

        # Header
        tk.Label(self.root, text="Admin Dashboard", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Logged in as: {self.username}", font=("Arial", 12)).pack(pady=5)

        # User Table
        self.tree = ttk.Treeview(self.root, columns=("Username", "Role"), show="headings", height=10)
        self.tree.heading("Username", text="Username")
        self.tree.heading("Role", text="Role")
        self.tree.pack(pady=10, fill=tk.X)

        # Buttons Container
        button_container = ttk.Frame(self.root)
        button_container.pack(pady=10, fill="x")

        button_row = ttk.Frame(button_container)
        button_row.pack(pady=10, anchor="center")
        ttk.Button(
            button_row, text="Add User", command=self.add_user, bootstyle="success", width=15
            ).pack(side="left", padx=10)

        ttk.Button(
            button_row, text="Delete User", command=self.delete_user, bootstyle="danger", width=15
        ).pack(side="left", padx=10)

        ttk.Button(
            button_row, text="View User Activity", command=self.view_user_activity, bootstyle="primary", width=15
        ).pack(side="left", padx=14)

        ttk.Button(
            button_row, text="Logout", command=self.logout, bootstyle="secondary", width=15
        ).pack(side="left", padx=10)

        self.load_users()


    def load_users(self):
        """Load all users from the database into the table."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        users = users_collection.find({})
        for user in users:
            username = user.get("username", "Unknown")
            role = user.get("role", "user")  # Default to 'user' if role is missing
            self.tree.insert("", tk.END, values=(username, role))

    def add_user(self):
        """Add a new user to the database."""
        username = tk.simpledialog.askstring("Add User", "Enter new username:")
        if not username:
            return

        if users_collection.find_one({"username": username}):
            messagebox.showerror("Error", "User already exists!")
            return

        role = tk.simpledialog.askstring("Add User", "Enter role (admin/user):")
        if role not in ["admin", "user"]:
            messagebox.showerror("Error", "Invalid role. Please enter 'admin' or 'user'.")
            return

        password = tk.simpledialog.askstring("Add User", "Enter password:", show="*")
        users_collection.insert_one({"username": username, "password": password, "role": role, "activities": []})
        messagebox.showinfo("Success", f"User '{username}' added successfully!")
        self.load_users()

    def delete_user(self):
        """Delete the selected user."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No user selected!")
            return

        username = self.tree.item(selected_item)["values"][0]
        if username == self.username:
            messagebox.showerror("Error", "You cannot delete yourself!")
            return

        users_collection.delete_one({"username": username})
        messagebox.showinfo("Success", f"User '{username}' deleted successfully!")
        self.load_users()

    def view_user_activity(self):
        """View activity logs for the selected user."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No user selected!")
            return

        username = self.tree.item(selected_item)["values"][0]
        user = users_collection.find_one({"username": username})
        if not user or "activities" not in user:
            messagebox.showinfo("No Data", f"No activities found for {username}.")
            return

        self.display_activity_logs(username, user["activities"])

    def display_activity_logs(self, username, activities):
        """Display activity logs for a specific user."""
        activity_window = tk.Toplevel(self.root)
        activity_window.title(f"{username} - Activity Logs")
        tk.Label(activity_window, text=f"Activity Logs for {username}", font=("Arial", 16)).pack(pady=10)

        # Scrollable container
        container_frame = tk.Frame(activity_window)
        container_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas and scrollbar
        canvas_widget = tk.Canvas(container_frame)
        scrollbar = tk.Scrollbar(container_frame, orient=tk.VERTICAL, command=canvas_widget.yview)
        scrollable_frame = tk.Frame(canvas_widget)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_widget.configure(scrollregion=canvas_widget.bbox("all"))
        )

        canvas_widget.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_widget.configure(yscrollcommand=scrollbar.set)

        canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.graph_images = []  # Store references to prevent garbage collection

        for activity in activities:
            # Display activity details
            total_time = activity.get("total_time", 0)
            active_time = activity.get("active_seconds", 0)

            time_unit = "seconds"
            if total_time > 3600:
                total_time /= 3600
                active_time /= 3600
                time_unit = "hours"
            elif total_time > 60:
                total_time /= 60
                active_time /= 60
                time_unit = "minutes"

            activity_details = (
                f"Date: {activity['date']} | "
                f"Start Time: {activity.get('start_time', 'N/A')} | "
                f"End Time: {activity.get('end_time', 'N/A')} | "
                f"Total Time: {total_time:.2f} {time_unit} | "
                f"Active Time: {active_time:.2f} {time_unit}"
            )

            tk.Label(scrollable_frame, text=activity_details, font=("Arial", 12), anchor="w").pack(fill=tk.X, pady=5)

            # Display graph if available
            graph_path = activity.get("graph")
            if graph_path:
                if os.path.exists(graph_path):
                    try:
                        # Load and resize the image
                        with Image.open(graph_path) as img:
                            img = img.resize(self.graph_size, Image.Resampling.LANCZOS)
                            graph_image = ImageTk.PhotoImage(img)
                            self.graph_images.append(graph_image)  # Keep reference
                            tk.Label(scrollable_frame, image=graph_image).pack(pady=5)
                    except Exception as e:
                        print(f"Error loading graph: {e}")
                else:
                    print(f"Graph not found at path: {graph_path}")

        # Button to download activities as a PDF
        tk.Button(activity_window, text="Download Activities as PDF", command=lambda: self.download_activities_as_pdf(username, activities)).pack(pady=10)

        # Close button
        tk.Button(activity_window, text="Close", command=activity_window.destroy).pack(pady=10)

    def download_activities_as_pdf(self, username, activities):
        """Generate and download a PDF of user activities."""
        # Prompt user to choose a save location
        file_path = asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{username}_activities.pdf"
        )
        if not file_path:
            return  # User cancelled the save operation

        # Create the PDF
        pdf_canvas = canvas.Canvas(file_path, pagesize=letter)
        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.drawString(50, 750, f"Activity Logs for User: {username}")
        pdf_canvas.drawString(50, 735, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf_canvas.line(50, 730, 550, 730)

        y_position = 710
        for activity in activities:
            if y_position < 50:  # Start a new page if the content reaches the bottom
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica", 12)
                y_position = 750

            total_time = activity.get("total_time", 0)
            active_time = activity.get("active_seconds", 0)

            time_unit = "seconds"
            if total_time > 3600:
                total_time /= 3600
                active_time /= 3600
                time_unit = "hours"
            elif total_time > 60:
                total_time /= 60
                active_time /= 60
                time_unit = "minutes"

            pdf_canvas.drawString(50, y_position, f"Date: {activity['date']}")
            y_position -= 15
            pdf_canvas.drawString(50, y_position, f"Start Time: {activity.get('start_time', 'N/A')} | End Time: {activity.get('end_time', 'N/A')}")
            y_position -= 15
            pdf_canvas.drawString(50, y_position, f"Total Time: {total_time:.2f} {time_unit} | Active Time: {active_time:.2f} {time_unit}")
            y_position -= 30

        # Save the PDF
        pdf_canvas.save()
        messagebox.showinfo("Success", f"Activities PDF saved to {file_path}")

    def logout(self):
        """Log the admin out."""
        self.app.logout()

    def clear_frame(self):
        """Clear all widgets from the current frame."""
        for widget in self.root.winfo_children():
            widget.destroy()
