from constants import app_name
from utils import list_project_entries, new_projectfile
import sys

class MenuOption:
	def __init__(self, name, command):
		self.name = name
		self.command = command
		
	def draw(self, s):
		print(self.name + " " * s + "(" + self.command + ")")

class Menu:
	def __init__(self, options):
		self.menuoptions = []
		for name, command in options:
			self.add_menu_option(name, command)

	def add_menu_option(self, name, command):
		new_opt = MenuOption(name, command)
		self.menuoptions.append(new_opt)

	def draw(self):
		l = []
		for opt in self.menuoptions:
			l.append(opt.name)
		m = max(map(len, l))
		#number of spaces to put after the name
		for opt in self.menuoptions:
			s = m - len(opt.name) + 1
			opt.draw(s)

class MainMenu(Menu):
	def __init__(self, options):
		
		super().__init__(options)

	def draw(self):
		print("")
		print("---------")
		super().draw()
		print("---------")
		print("")

	def show(self):
		self.draw()
		while True:
			i = input(" > ")
			if on_input(i) is False:
				break
#______________
def list_projects():
	print("Here's a list of your projects: ")
	print("---------")
	list_project_entries()
	print("---------")

def open_project():
	print("Project <projectname> was opened")

def create_project():
	file = new_projectfile()
	print("Project " + file.name + " was created")

def delete_project():
	print("Project <projectname> was deleted")

def exit_mainmenu():
	return False
#______________
def on_input(input):
	if input == "list":
		list_projects()
		
	elif input == "open":
		open_project()
		
	elif input == "new":
		create_project()
		
	elif input == "delete":
		delete_project()
		
	elif input == "exit":
		return exit_mainmenu()
		
	else:
		print("Error: Unrecognized command")

def enter_mainmenu():
	main_menu_options = [("List projects", "list"),("Open project", "open"),("Create new project", "new"),("Delete project", "delete"),("Exit " + app_name, "exit")]
	main_menu = MainMenu(main_menu_options)
	main_menu.show()
	return
