import customtkinter as ctk
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import json

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Habit:
    def __init__(self, name):
        self.name = name
        self.count = 0
        self.schedules = []

    def increment(self):
        self.count += 1

    def add_schedule(self, time):
        if time not in self.schedules:
            self.schedules.append(time)
            self.schedules.sort()


class Category:
    def __init__(self, name):
        self.name = name
        self.habits = {}

    def add_habit(self, habit):
        if habit.name not in self.habits:
            self.habits[habit.name] = habit
            return True
        return False

    def remove_habit(self, name):
        if name in self.habits:
            del self.habits[name]
            return True
        return False


class HabitTracker:
    def __init__(self):
        self.categories = {}

    def add_category(self, name):
        if name and name not in self.categories:
            self.categories[name] = Category(name)
            return True
        return False

    def remove_category(self, name):
        if name in self.categories:
            del self.categories[name]
            return True
        return False

    def add_habit(self, category_name, habit_name):
        if category_name in self.categories:
            habit = Habit(habit_name)
            return self.categories[category_name].add_habit(habit)
        return False

    def remove_habit(self, category_name, habit_name):
        if category_name in self.categories:
            return self.categories[category_name].remove_habit(habit_name)
        return False

    def save_to_json(self, filename):
        data = {}
        for cat_name, category in self.categories.items():
            data[cat_name] = {
                "habits": {
                    habit.name: {"count": habit.count,
                                 "schedules": habit.schedules}
                    for habit in category.habits.values()
                }
            }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_from_json(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.categories.clear()
            for cat_name, cat_data in data.items():
                self.add_category(cat_name)
                for habit_name, habit_data in cat_data["habits"].items():
                    habit = Habit(habit_name)
                    habit.count = habit_data["count"]
                    habit.schedules = habit_data["schedules"]
                    self.categories[cat_name].habits[habit_name] = habit
            return True
        except FileNotFoundError:
            return False


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Phantom's Habit Tracker")
        self.geometry("1000x600")
        self.habit_tracker = HabitTracker()
        self.load_data()
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Habit Section
        self.habit_frame = ctk.CTkFrame(self)
        self.habit_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.habit_frame.grid_columnconfigure(0, weight=1)
        self.habit_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.habit_frame, text="Habits", font=(
            "Arial", 24, "bold")).grid(row=0, column=0, pady=10)

        self.create_habit_input_frame()

        self.categories_frame = ctk.CTkScrollableFrame(self.habit_frame)
        self.categories_frame.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Schedule Section
        self.schedule_frame = ctk.CTkFrame(self)
        self.schedule_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.schedule_frame.grid_columnconfigure(0, weight=1)
        self.schedule_frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self.schedule_frame, text="Schedules", font=(
            "Arial", 24, "bold")).grid(row=0, column=0, pady=10)

        self.create_schedule_input_frame()

        self.schedule_list = ctk.CTkTextbox(self.schedule_frame)
        self.schedule_list.grid(
            row=3, column=0, sticky="nsew", padx=10, pady=10)

        self.update_category_list()
        self.update_schedule_list()

    def create_habit_input_frame(self):
        input_frame = ctk.CTkFrame(self.habit_frame)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.category_input = ctk.CTkEntry(
            input_frame, placeholder_text="Enter category name")
        self.category_input.grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(input_frame, text="Add Category", command=self.add_category).grid(
            row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(input_frame, text="Remove Category", command=self.remove_category).grid(
            row=0, column=3, padx=5, pady=5, sticky="ew")

        self.habit_input = ctk.CTkEntry(
            input_frame, placeholder_text="Enter habit")
        self.habit_input.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.category_select = ctk.CTkOptionMenu(input_frame, values=[])
        self.category_select.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(input_frame, text="Add Habit", command=self.add_habit).grid(
            row=1, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(input_frame, text="Remove Habit", command=self.remove_habit).grid(
            row=1, column=3, padx=5, pady=5, sticky="ew")

    def create_schedule_input_frame(self):
        input_frame = ctk.CTkFrame(self.schedule_frame)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.schedule_habit_input = ctk.CTkEntry(
            input_frame, placeholder_text="Enter habit name")
        self.schedule_habit_input.grid(
            row=0, column=0, padx=5, pady=5, sticky="ew")

        self.schedule_time_input = ctk.CTkEntry(
            input_frame, placeholder_text="Enter time (HH:MM)")
        self.schedule_time_input.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(input_frame, text="Add Schedule", command=self.add_schedule).grid(
            row=0, column=2, padx=5, pady=5, sticky="ew")

    def add_category(self):
        category_name = self.category_input.get().strip()
        if self.habit_tracker.add_category(category_name):
            self.update_category_list()
            self.category_input.delete(0, 'end')
            self.save_data()
        else:
            self.show_error("Category already exists or invalid name.")

    def remove_category(self):
        category_name = self.category_select.get()
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the category '{category_name}' and all its habits?"):
            if self.habit_tracker.remove_category(category_name):
                self.update_category_list()
                self.update_schedule_list()
                self.save_data()
            else:
                self.show_error("Failed to remove category.")

    def add_habit(self):
        habit_name = self.habit_input.get().strip()
        category_name = self.category_select.get()
        if self.habit_tracker.add_habit(category_name, habit_name):
            self.update_category_list()
            self.habit_input.delete(0, 'end')
            self.save_data()
        else:
            self.show_error("Habit already exists or invalid name.")

    def remove_habit(self):
        habit_name = self.habit_input.get().strip()
        category_name = self.category_select.get()
        if self.habit_tracker.remove_habit(category_name, habit_name):
            self.update_category_list()
            self.update_schedule_list()
            self.habit_input.delete(0, 'end')
            self.save_data()
        else:
            self.show_error("Habit not found or invalid name.")

    def update_category_list(self):
        for widget in self.categories_frame.winfo_children():
            widget.destroy()

        category_names = list(self.habit_tracker.categories.keys())
        self.category_select.configure(values=category_names)
        if category_names:
            self.category_select.set(category_names[0])
        else:
            self.category_select.set("")

        for category_name, category in self.habit_tracker.categories.items():
            category_frame = ctk.CTkFrame(self.categories_frame)
            category_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(category_frame, text=category_name,
                         font=("Arial", 18, "bold")).pack()

            for habit_name, habit in category.habits.items():
                habit_frame = ctk.CTkFrame(category_frame)
                habit_frame.pack(fill="x", padx=5, pady=2)

                habit_info = f"{habit_name} - Count: {habit.count}"
                if habit.schedules:
                    habit_info += f" | Schedules: {', '.join(habit.schedules)}"

                ctk.CTkLabel(habit_frame, text=habit_info, wraplength=400,
                             justify="left").pack(side="left", padx=5)
                ctk.CTkButton(habit_frame, text="Finished", command=lambda h=habit: self.increment_habit(
                    h)).pack(side="right", padx=5)

    def increment_habit(self, habit):
        habit.increment()
        self.update_category_list()
        self.save_data()

    def add_schedule(self):
        habit_name = self.schedule_habit_input.get().strip()
        time = self.schedule_time_input.get().strip()

        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            self.show_error("Invalid time format. Please use HH:MM.")
            return

        for category in self.habit_tracker.categories.values():
            if habit_name in category.habits:
                category.habits[habit_name].add_schedule(time)
                self.update_category_list()
                self.update_schedule_list()
                self.schedule_habit_input.delete(0, 'end')
                self.schedule_time_input.delete(0, 'end')
                self.save_data()
                return

        self.show_error("Habit not found.")

    def update_schedule_list(self):
        self.schedule_list.delete("1.0", "end")
        for category in self.habit_tracker.categories.values():
            for habit in category.habits.values():
                for time in habit.schedules:
                    self.schedule_list.insert(
                        "end", f"{habit.name} - Time: {time}\n")

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def save_data(self):
        self.habit_tracker.save_to_json("habit_data.json")

    def load_data(self):
        if not self.habit_tracker.load_from_json("habit_data.json"):
            messagebox.showinfo(
                "Welcome", "Welcome to Phantom's Habit Tracker!")


if __name__ == "__main__":
    app = App()
    app.mainloop()
