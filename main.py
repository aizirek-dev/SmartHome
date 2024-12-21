from abc import ABC, abstractmethod
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import time
from datetime import datetime, timedelta

class SmartDevice(ABC):
    def __init__(self, name):
        self.name = name
        self.is_on = False
        self.status = "выключен"

    def turn_on(self):
        self.is_on = True
        self.status = "включен"
        return f"{self.name} включено."

    def turn_off(self):
        self.is_on = False
        self.status = "выключен"
        return f"{self.name} выключено."

    @abstractmethod
    def perform_action(self):
        pass


class Light(SmartDevice):
    def __init__(self, name):
        super().__init__(name)
        self.temperature = 22

    def set_temperature(self, temp):
        self.temperature = temp
        return f"{self.name}: Температура установлена на {temp}°C."

    def perform_action(self):
        return f"{self.name}: свет {'включен' if self.is_on else 'выключен'}, температура {self.temperature}°C."

class Kettle(SmartDevice):
    def perform_action(self):
        if self.is_on:
            self.status = "кипятится"
            Thread(target=self.boil).start()
            return f"{self.name}: Включен для кипячения."
        else:
            return f"{self.name}: Выключен."

    def boil(self):
        time.sleep(10)
        self.status = "готов"
        messagebox.showinfo("Уведомление", "Чайник вскипел. Приятного чаепития!")

    def schedule_boil(self, delay_minutes):
        Thread(target=self.delayed_boil, args=(delay_minutes,)).start()

    def delayed_boil(self, delay_minutes):
        time.sleep(delay_minutes * 60)
        self.turn_on()
        self.boil()

class Bath(SmartDevice):
    def __init__(self, name):
        super().__init__(name)
        self.water_temperature = None
        self.is_filled = False

    def set_temperature(self, temperature):
        self.water_temperature = temperature
        return f"{self.name}: Температура воды установлена на {temperature}°C."

    def perform_action(self):
        if not self.is_filled:
            if self.water_temperature is None:
                return f"{self.name}: Пожалуйста, установите температуру перед наполнением."
            self.status = "заполняется"
            Thread(target=self.fill_bath).start()
            return f"{self.name}: Включена для наполнения водой."
        else:
            self.is_filled = False
            self.status = "пустая"
            return f"{self.name}: Вода слита."

    def fill_bath(self):
        time.sleep(10)
        self.is_filled = True
        self.status = "готова"
        messagebox.showinfo("Уведомление", "Ванна наполнена. Приятного отдыха!")

class Door(SmartDevice):
    def lock(self):
        self.status = "заперта"
        return f"{self.name} заперта."

    def unlock(self):
        self.status = "отперта"
        return f"{self.name} отперта."

    def perform_action(self):
        return f"{self.name}: дверь {self.status}."


class SmartHome:
    def __init__(self):
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)

    def status_report(self):
        report = ""
        for device in self.devices:
            if isinstance(device, Light):
                report += f"{device.name}: свет - {device.status}, температура {device.temperature}°C\n"
            elif isinstance(device, Bath):
                report += f"{device.name}: ванна - {device.status}, температура воды - {device.water_temperature}°C\n"
            elif isinstance(device, Kettle):
                report += f"{device.name}: чайник - {device.status}\n"
            elif isinstance(device, Door):
                report += f"{device.name}: дверь - {device.status}\n"
        return report

def create_gui():
    home = SmartHome()

    # Devices
    light1 = Light("Спальня")
    light2 = Light("Кухня")
    light3 = Light("Зал")
    bath = Bath("Ванна")
    kettle = Kettle("Чайник")
    door = Door("Входная дверь")

    home.add_device(light1)
    home.add_device(light2)
    home.add_device(light3)
    home.add_device(bath)
    home.add_device(kettle)
    home.add_device(door)

    def show_main_menu():
        for widget in window.winfo_children():
            widget.destroy()

        tk.Label(window, text="Добро пожаловать в Умный Дом!", font=("Helvetica", 16), pady=20).pack()
        tk.Button(window, text="Мой умный дом", command=show_device_menu, height=3, width=30).pack(pady=10)
        tk.Button(window, text="Показать статус", command=show_status, height=3, width=30).pack(pady=10)

    def show_device_menu():
        for widget in window.winfo_children():
            widget.destroy()

        tk.Label(window, text="Выберите устройство:", font=("Helvetica", 14), pady=10).pack()
        device_var = tk.StringVar(value="Спальня")
        tk.OptionMenu(window, device_var, *[d.name for d in home.devices]).pack(pady=10)
        tk.Button(window, text="Выбрать", command=lambda: show_device_actions(device_var.get()), height=2, width=20).pack(pady=20)

    def show_device_actions(device_name):
        for widget in window.winfo_children():
            widget.destroy()

        device = next(d for d in home.devices if d.name == device_name)

        tk.Label(window, text=f"Устройство: {device.name}", font=("Helvetica", 14), pady=10).pack()

        if isinstance(device, Light):
            tk.Button(window, text="Включить свет", command=lambda: control_device(device, "on"), height=2, width=20).pack(pady=5)
            tk.Button(window, text="Выключить свет", command=lambda: control_device(device, "off"), height=2, width=20).pack(pady=5)
            tk.Scale(window, from_=10, to=30, orient=tk.HORIZONTAL, label="Температура комнаты", command=lambda t: device.set_temperature(int(t))).pack(pady=10)
        elif isinstance(device, Bath):
            tk.Scale(window, from_=0, to=80, orient=tk.HORIZONTAL, label="Температура воды", command=lambda temp: device.set_temperature(int(temp))).pack(pady=10)
            tk.Button(window, text="Заполнить ванну", command=lambda: perform_action(device), height=2, width=20).pack(pady=5)
            tk.Button(window, text="Слить воду", command=lambda: perform_action(device), height=2, width=20).pack(pady=5)
        elif isinstance(device, Kettle):
            tk.Button(window, text="Включить чайник", command=lambda: control_device(device, "on"), height=2, width=20).pack(pady=5)
            tk.Button(window, text="Выключить чайник", command=lambda: control_device(device, "off"), height=2, width=20).pack(pady=5)

            def schedule_kettle():
                try:
                    delay_minutes = int(schedule_entry.get())
                    device.schedule_boil(delay_minutes)
                    messagebox.showinfo("Результат", f"{device.name}: будет включён через {delay_minutes} минут.")
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректное число.")

            tk.Label(window, text="Запланировать включение через (мин):").pack(pady=5)
            schedule_entry = tk.Entry(window)
            schedule_entry.pack(pady=5)
            tk.Button(window, text="Запланировать", command=schedule_kettle, height=2, width=20).pack(pady=5)
        elif isinstance(device, Door):
            tk.Button(window, text="Запереть дверь", command=lambda: lock_unlock_door(device, "lock"), height=2, width=20).pack(pady=5)
            tk.Button(window, text="Отпереть дверь", command=lambda: lock_unlock_door(device, "unlock"), height=2, width=20).pack(pady=5)

        tk.Button(window, text="Вернуться в главное меню", command=show_main_menu, height=3, width=30).pack(pady=20)

    def control_device(device, action):
        if action == "on":
            messagebox.showinfo("Результат", device.turn_on())
        elif action == "off":
            messagebox.showinfo("Результат", device.turn_off())

    def lock_unlock_door(device, action):
        if action == "lock":
            messagebox.showinfo("Результат", device.lock())
        elif action == "unlock":
            messagebox.showinfo("Результат", device.unlock())

    def perform_action(device):
        messagebox.showinfo("Результат", device.perform_action())

    def show_status():
        messagebox.showinfo("Статус", home.status_report())

    window = tk.Tk()
    window.title("Управление умным домом")
    window.geometry("400x600")

    show_main_menu()

    window.mainloop()

if __name__ == "__main__":
    create_gui()
