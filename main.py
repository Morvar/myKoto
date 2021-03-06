#!/usr/bin/env python
# coding: utf-8
import sys
from mainmenu import MainMenu
import constants
import utils
from scene import Scene

#do stuff that needs to be done before exiting the app, then exit
def exit_application():
	print("Exiting " + constants.app_name + " now. Cya!")
	sys.exit(0)

#do necessary setup
def init_app():
	utils.init_project_dir()

#this is the ENTRY POINT
if __name__ == "__main__":
	#if main was run with argument 'd', enable debug mode
	if len(sys.argv) > 1 and sys.argv[1] == 'd':
		constants.debug = True
	#do necessary setup
	init_app()
	print("Welcome to " + constants.app_name + "!")
	if constants.debug: print("DEBUG MODE ENABLED")
	#create a main menu and enter it
	main_menu = MainMenu()
	while True:
		main_menu.enter()
		# when main menu returns, the user has chosen to exit the application
		exit_application()
