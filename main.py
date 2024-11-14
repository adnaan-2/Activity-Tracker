import tkinter as tk
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from pages.user_dashboard_page import UserDashboardPage
from pages.admin_dashboard_page import AdminDashboardPage

class EmployeeTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")  # Set the window size
        self.current_user = None
        self.show_login()  # Initially show the login page

    def show_login(self):
        # Clears the frame and shows the login page
        self.clear_frame()
        login_page = LoginPage(self.root, self)  # Create the LoginPage object
        login_page.show()  # Show the login page

    def show_signup(self):
        # Clears the frame and shows the signup page
        self.clear_frame()
        signup_page = SignupPage(self.root, self)  # Create the SignupPage object
        signup_page.show()  # Show the signup page

    def show_user_dashboard(self, username):
        # Clears the frame and shows the user dashboard
        self.clear_frame()
        self.current_user = username  # Save the current user's username
        user_dashboard = UserDashboardPage(self.root, self, username)  # Create the UserDashboardPage object
        user_dashboard.show()  # Show the user dashboard

    def show_admin_dashboard(self, username):
        # Clears the frame and shows the admin dashboard
        self.clear_frame()
        self.current_user = username  # Save the current admin's username
        admin_dashboard = AdminDashboardPage(self.root, self, username)  # Create the AdminDashboardPage object
        admin_dashboard.show()  # Show the admin dashboard

    def logout(self):
        # Logout the user and show the login page again
        self.current_user = None
        self.show_login()  # Return to the login screen

    def clear_frame(self):
        # Clears all widgets in the current frame
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeTrackingApp(root)
    root.mainloop()
