import tkinter as tk
from tkinter import messagebox
from threading import Thread
import keyboard
import mouse
import time
import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db import users_collection
from utils.auth import change_password


class UserDashboardPage:
    def __init__(self, root, app, username):
        self.root = root
        self.app = app
        self.username = username
        self.monitoring = False
        self.start_time = None
        self.active_seconds = 0
        self.rest_seconds = 0
        self.activity_detected = False
        self.graph_frame = None  # Frame to hold the graph
        self.graph_directory = "graphs"
        os.makedirs(self.graph_directory, exist_ok=True)

    def show(self):
        self.clear_frame()

        # Header Section
        header = tk.Frame(self.root, bg="lightgray", height=50)
        header.pack(fill="x")
        tk.Label(header, text=f"Hi there, {self.username}", bg="lightgray", font=("Arial", 14)).pack(side="left", padx=10)
        tk.Label(header, text="Employee Tracking System", bg="lightgray", font=("Arial", 14, "bold")).pack(side="left", expand=True)

        # Dropdown Menu for Logout and other options
        menu_button = tk.Menubutton(header, text="Options", relief="raised", bg="gray", fg="white")
        menu = tk.Menu(menu_button, tearoff=0)
        menu.add_command(label="View Activity", command=self.view_activity)
        menu.add_command(label="Logout", command=self.logout)
        menu.add_command(label="Reset Password", command=self.reset_password_dialog)
        menu_button.config(menu=menu)
        menu_button.pack(side="right", padx=10)

        # Dashboard Content
        tk.Label(self.root, text="Welcome to User Dashboard", font=("Arial", 20)).pack(pady=20)

        # Time Display Containers in a Single Row
        time_container = tk.Frame(self.root)
        time_container.pack(pady=10, fill="x")

        # Current Date Container
        date_frame = tk.Frame(time_container, bg="lightblue", padx=20, pady=10)
        date_frame.pack(side="left", expand=True, fill="both")
        tk.Label(date_frame, text="Current Date", font=("Arial", 12, "bold"), bg="lightblue").pack()
        self.current_date_label = tk.Label(date_frame, text=datetime.date.today().isoformat(), font=("Arial", 12), bg="lightblue")
        self.current_date_label.pack()

        # Activity Time Container
        activity_frame = tk.Frame(time_container, bg="lightgreen", padx=20, pady=10)
        activity_frame.pack(side="left", expand=True, fill="both")
        tk.Label(activity_frame, text="Activity Time", font=("Arial", 12, "bold"), bg="lightgreen").pack()
        self.activity_time_label = tk.Label(activity_frame, text="00:00:00", font=("Arial", 12), bg="lightgreen")
        self.activity_time_label.pack()

        # Rest Time Container
        rest_frame = tk.Frame(time_container, bg="lightcoral", padx=20, pady=10)
        rest_frame.pack(side="left", expand=True, fill="both")
        tk.Label(rest_frame, text="Rest Time", font=("Arial", 12, "bold"), bg="lightcoral").pack()
        self.rest_time_label = tk.Label(rest_frame, text="00:00:00", font=("Arial", 12), bg="lightcoral")
        self.rest_time_label.pack()

        # Start and End Activity Buttons
        tk.Button(self.root, text="Start Monitoring", command=self.start_monitoring, bg="green", fg="white", width=15, height=2).pack(pady=10)
        tk.Button(self.root, text="Stop Monitoring", command=self.stop_monitoring, bg="red", fg="white", width=15, height=2).pack(pady=10)

        # Graph Frame
        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.pack(fill="both", expand=True)
    
    def reset_password_dialog(self):
        # Create a new top-level window for resetting the password
        reset_pw_window = tk.Toplevel(self.root)
        reset_pw_window.title("Reset Password")
        reset_pw_window.geometry("400x250")

        # Add input fields for the old and new passwords
        tk.Label(reset_pw_window, text="Current Password:").pack(pady=10)
        current_password_entry = tk.Entry(reset_pw_window, show="*")
        current_password_entry.pack(pady=5)

        tk.Label(reset_pw_window, text="New Password:").pack(pady=10)
        new_password_entry = tk.Entry(reset_pw_window, show="*")
        new_password_entry.pack(pady=5)

        tk.Label(reset_pw_window, text="Confirm New Password:").pack(pady=10)
        confirm_password_entry = tk.Entry(reset_pw_window, show="*")
        confirm_password_entry.pack(pady=5)

        def submit_reset():
            # Get the current, new, and confirm passwords from the user
            current_password = current_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            # Check if the fields are not empty
            if not current_password or not new_password or not confirm_password:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            # Validate the current password and change to the new password
            if not change_password(self.username, current_password, new_password):
                messagebox.showerror("Error", "Current password is incorrect.")
                return

            if new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match.")
                return

            # If everything is valid, reset the password
            messagebox.showinfo("Success", "Password reset successfully!")
            reset_pw_window.destroy()

        # Add a submit button to trigger the password change
        submit_button = tk.Button(reset_pw_window, text="Submit", command=submit_reset)
        submit_button.pack(pady=20)

    def view_activity(self):
        """Fetch and display the activity logs for the logged-in user, including graphs."""
        user = users_collection.find_one({"username": self.username})
        if not user or "activities" not in user:
            messagebox.showinfo("No Activity", f"No activity logs found for {self.username}.")
            return

        # Create a new window to display activity logs
        activity_window = tk.Toplevel(self.root)
        activity_window.title(f"Activity Logs - {self.username}")
        activity_window.geometry("800x600")

        # Create a scrollable frame
        canvas = tk.Canvas(activity_window)
        scroll_y = tk.Scrollbar(activity_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Display each activity log
        for i, activity in enumerate(user["activities"], start=1):
            log_frame = tk.Frame(scrollable_frame, bg="white", relief="solid", borderwidth=1, padx=10, pady=5)
            log_frame.pack(fill="x", pady=10)

            # Display activity details
            tk.Label(log_frame, text=f"Log {i}", font=("Arial", 12, "bold")).pack(anchor="w")
            tk.Label(log_frame, text=f"Date: {activity['date']}", font=("Arial", 10)).pack(anchor="w")
            tk.Label(log_frame, text=f"Start Time: {activity['start_time']}", font=("Arial", 10)).pack(anchor="w")
            tk.Label(log_frame, text=f"End Time: {activity['end_time']}", font=("Arial", 10)).pack(anchor="w")
            tk.Label(log_frame, text=f"Active Time: {activity['active_seconds']} seconds", font=("Arial", 10)).pack(anchor="w")
            tk.Label(log_frame, text=f"Rest Time: {activity['rest_seconds']} seconds", font=("Arial", 10)).pack(anchor="w")

            # Display graph if available
            graph_path = activity.get("graph")
            if os.path.exists(graph_path):  # Check if graph file exists
                tk.Label(log_frame, text="Activity Graph:", font=("Arial", 10, "bold")).pack(anchor="w")
                fig = plt.figure(figsize=(5, 3))
                img = plt.imread(graph_path)
                plt.imshow(img)
                plt.axis("off")

                # Embed the graph into the Tkinter window
                canvas_graph = FigureCanvasTkAgg(fig, master=log_frame)
                canvas_graph.draw()
                canvas_graph.get_tk_widget().pack(fill="x", expand=True)
                plt.close(fig)  # Close the figure to free memory
            else:
                tk.Label(log_frame, text="Graph not available.", font=("Arial", 10, "italic"), fg="red").pack(anchor="w")

            # Separator between logs
            tk.Label(log_frame, text="-" * 100, fg="gray").pack(anchor="w")

        # Add a close button
        tk.Button(activity_window, text="Close", command=activity_window.destroy).pack(pady=10)



    def start_monitoring(self):
        if self.monitoring:
            messagebox.showinfo("Monitoring", "Monitoring is already running!")
            return

        self.monitoring = True
        self.start_time = time.time()
        self.active_seconds = 0
        self.rest_seconds = 0
        Thread(target=self.monitor_activity, daemon=True).start()
        Thread(target=self.update_dashboard, daemon=True).start()

    

    def stop_monitoring(self):
        if not self.monitoring:
            messagebox.showinfo("Monitoring", "Monitoring is not running!")
            return

        self.monitoring = False
        self.save_activity_to_db()
        self.display_graph()
        messagebox.showinfo("Monitoring", "Monitoring stopped and data saved!")

    def monitor_activity(self):
        last_active_time = time.time()

        def mark_activity(event=None):
            self.activity_detected = True

        keyboard.hook(mark_activity)
        mouse.hook(mark_activity)

        try:
            while self.monitoring:
                time.sleep(1)
                if self.activity_detected:
                    self.active_seconds += 1
                    last_active_time = time.time()
                    self.activity_detected = False
                elif time.time() - last_active_time >= 1:
                    self.rest_seconds += 1
        finally:
            keyboard.unhook(mark_activity)
            mouse.unhook(mark_activity)

    def update_dashboard(self):
        while self.monitoring:
            active_hr, active_min, active_sec = self.format_time(self.active_seconds)
            rest_hr, rest_min, rest_sec = self.format_time(self.rest_seconds)
            self.activity_time_label.config(text=f"Hr {active_hr}: Min {active_min}: Sec {active_sec}")
            self.rest_time_label.config(text=f"Hr {rest_hr}: Min {rest_min}: Sec {rest_sec}")
            elapsed_time = int(time.time() - self.start_time)
            self.current_date_label.config(text=f"Elapsed Time: {elapsed_time} seconds")
            time.sleep(1)

    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return hours, minutes, seconds

    def save_activity_to_db(self):
        date = datetime.date.today().isoformat()
        total_time = self.active_seconds + self.rest_seconds

        activity_log = {
            "date": date,
            "start_time": datetime.datetime.fromtimestamp(self.start_time).strftime("%H:%M:%S"),
            "end_time": datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S"),
            "active_seconds": self.active_seconds,
            "rest_seconds": self.rest_seconds,
            "total_time": total_time,
            "graph": f"{self.graph_directory}/{self.username}_{date}.png"
        }

        users_collection.update_one(
            {"username": self.username},
            {"$push": {"activities": activity_log}},
            upsert=True
        )

    def display_graph(self):
        date = datetime.date.today().isoformat()
        total_time = self.active_seconds + self.rest_seconds

        # Convert time to minutes or hours if appropriate
        active_time = self.active_seconds
        time_unit = "Seconds"
        if total_time > 3600:
            active_time /= 3600
            total_time /= 3600
            time_unit = "Hours"
        elif total_time > 60:
            active_time /= 60
            total_time /= 60
            time_unit = "Minutes"

        # Generate the graph
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Total Time", "Active Time"], [total_time, active_time], color=["blue", "green"])
        ax.set_title(f"Activity Graph for {self.username} ({date})")
        ax.set_ylabel(f"Time ({time_unit})")
        ax.set_xlabel("Category")

        # Save graph
        graph_path = f"{self.graph_directory}/{self.username}_{date}.png"
        plt.savefig(graph_path)

        # Display graph in the dashboard
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def logout(self):
        self.stop_monitoring()  # Make sure monitoring is stopped
        self.app.show_login()  # Show the login page again (use show_login, not show_login_page)


    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
