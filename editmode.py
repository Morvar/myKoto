# coding: utf-8
from collections import OrderedDict
from scene import Scene, command
from buildmode import BuildMode
import constants
import utils
import re
import fnmatch
import pprint
from functools import reduce
import operator
#temporary debug
import traceback

class EditMode(Scene):
	def __init__(self, project_path):
		#construct a scene
		title = "Edit Mode"
		super().__init__(title)
		self.project_path = project_path
		self.project = utils.load_project(project_path)
		self.project_name = self.project.get("name", "")
		self.wordlist = self.project.get("wordlist", [])
		self.searchable_forms = self.project.get("searchable_forms", ["dictionary_form"])
		#put the project title in the title of the scene
		self.title = f"{title} [{self.project_name}]"
		self.unsaved = False

	if constants.debug:
		print("unsaved: " + str(self.unsaved))

	#specify the functions
	@command("buildmode", "Enter Build Mode")
	def enter_buildmode(self, args):
		buildmode = BuildMode()
		buildmode.enter()
		# is drawing scene a sane thing to do here?
		self.draw()
		return

	@command("show", "Show matches")
	def show(self, args):
		#if there were more than one additional argument, don't execute
		if len(args) > 1:
			utils.print_invalid_arg(args[1])
			return
		#if no argument default to '*', otherwise take the argument as search pattern
		search_pattern = args[0] if args else '*'
		#perform the search
		results = self.search(search_pattern)
		#if there were no matches, print and terminate
		if not results:
			print(f"No matches found for '{search_pattern}'")
			return
		#function for printing the results
		def printSearchresults(results):
			for (index, entry) in enumerate(results):
				result_dictionary_form = entry["dictionary_form"]
				print(f"[{index}] {result_dictionary_form}")
			#print("\n".join(entry["dictionary_form"] for entry in results))
		print(f"Showing matches for '{search_pattern}':")
		#print the results
		printSearchresults(results)

		#offer options to further inspect and edit the results
		while True:
			print("'view <index>' to view entry, 'edit <index>' to edit entry\n(enter empty line when done)")
			i = input(constants.input_prompt_nested_mode).split()
			#if no command was given, break
			if not i:
				break
			input_command = i[0]
			#if the command given was not one of the options, continue
			if not (input_command == "view" or input_command == "edit"):
				utils.print_invalid_arg(input_command)
				continue
			tail_args = i[1:]
			#if no index was provided, continue
			if not tail_args:
				utils.print_missing_arg("index")
				continue
			#if too many arguments were provided, continue
			if len(tail_args) > 1:
				utils.print_invalid_arg(tail_args[1])
				continue
			try:
				index = int(tail_args[0])
			except ValueError:
				#if the index provided could not be converted to an int, continue
				utils.print_invalid_arg(tail_args[0])
				continue

			#if index not one of the options presented to user, continue
			if index < 0 or index > len(results) - 1:
				utils.print_invalid_arg(str(index))
				continue
			#retrieve the entry TODO is this really what happens?
			entry = results[index]
			if input_command == "view":
				#view the entry
				self.print_entry_details(entry)
				continue

			elif input_command == "edit":
				while True:
					#edit the entry
					print("'<key> <subkey> <subsubkey> <...> <word>' to add a new or update an existing attribute\n(enter empty line when done)")
					i = input(constants.input_prompt_nested_mode).split()
					#if no command was given, break
					if not i:
						break
					if len(i) < 2:
						utils.print_missing_arg("word")
						continue
					#all but the last arg
					keys = i[:-1]
					#the last arg
					new_word = i[-1]
					#check if it already exists
					try:
						old_entry = reduce(operator.getitem, keys, entry)
					except KeyError:
						already_existing = False
					else:
						already_existing = True
					reduce(operator.getitem, keys[:-1], entry)[keys[-1]] = new_word
					self.unsaved = True
					if already_existing:
						print(f"Changed '{old_entry}' to '{new_word}'")
					else:
						print(f"Added '{new_word}'")
			else:
				#this is not supposed to happen anyway
				utils.print_invalid_arg(input_command)
				continue

	def print_entry_details(self, entry):
		pprint.pprint(entry)

#	@command("show", "Show entry")
#	def show(self, args):
		#if no arguments were given, don't execute
#		if not args:
#			utils.print_missing_arg("entry to show")
#			return
		#if there were more than one additional argument, don't execute
#		if len(args) > 1:
#			utils.print_invalid_arg(args[1])
#			return
		#extract the information from the entry passed
#		entry = args[0]
#		print(f"{entry}")

#	@command("edit", "Edit entry")
#	def edit(self, args):
#		pass

	@command("add", "Add entry")
	def add(self, args):
		#if no arguments were given, don't execute
		if not args:
			utils.print_missing_arg("dictionary form")
			return
		#if there were more than one additional argument, don't execute
		if len(args) > 1:
			utils.print_invalid_arg(args[1])
			return
		dictionary_form = args[0].strip()
		if self.word_exists(dictionary_form):
			print(f"Error: Word '{dictionary_form}' is already in the wordlist")
			return
		print("Part of speech (leave empty if not applicable): ")
		part_of_speech = input(constants.input_prompt_nested_mode).strip().lower()
		print("Meaning (leave empty if not applicable): ")
		meaning = input(constants.input_prompt_nested_mode).strip()
		print("Conjugation class (leave empty if not applicable): ")
		conjugation_class = input(constants.input_prompt_nested_mode).strip()
		print("Stem (leave empty if not applicable): ")
		stem = input(constants.input_prompt_nested_mode).strip()

		def additionalForms():
			forms = {}
			print("Add additional forms. These will override any general rules\n(enter empty line when done)")
			while True:
				print("Label: ")
				l = input(constants.input_prompt_nested_mode).strip()
				if not l:
					break
				else:
					print("Form: ")
					f = input(constants.input_prompt_nested_mode).strip()
					if not f:
						break
				forms[l] = f
				#temporarily add the form to searchable forms per default
				if l not in self.searchable_forms:
					self.searchable_forms.append(l)
				print("Added new form: " + l + " : " + f)
			return forms

		forms = additionalForms()
		conjugation = {}
		conjugation["conjugation_class"] = conjugation_class
		conjugation["stem"] = stem
		conjugation.update(forms)
		new_entry = wordlist_entry(dictionary_form, conjugation, part_of_speech, meaning)
		self.wordlist.append(new_entry)
		print("Added " + dictionary_form + " to word list")
		print("Part of speech:", part_of_speech)
		print("Meaning:", meaning)
		print("Conjugation class:", conjugation_class)
		print("Forms:",str(forms))
		self.unsaved = True
		if constants.debug:
			print("unsaved: " + str(self.unsaved))

	@command("save", "Save project")
	def save(self, args):
		if constants.debug:
			print(f"unsaved: {str(self.unsaved)}")
		#if there were additional arguments, don't execute
		if len(args):
			utils.print_invalid_arg(args[0])
			return
		utils.save_project(self.project, self.project_path)
		self.unsaved = False
		if constants.debug:
			print(f"unsaved: {str(self.unsaved)}")

	@command("exit", "Exit")
	def exit_editmode(self, args):
		if constants.debug:
			print(f"unsaved: {str(self.unsaved)}")
		if self.unsaved:
			while True:
				print("Do you want to save before exiting " + self.title + "? (yes/no)")
				i = input(constants.input_prompt)
				if i == "yes":
					utils.save_project(self.project, self.project_path)
					return False
				if i == "no":
					break
				else:
					print("Error: Unrecognized command")
		return False

	#helper functions for the editmode class

	def get_form(self, word, form):
		if form == "dictionary_form":
			return word["dictionary_form"]
		#if the word has no "conjugation", return None
		# and if the word has "conjugation" but not the specific form, return None
		return word.get("conjugation", {}).get(form, None)

	def word_exists(self, dictionary_form):
		for word in self.wordlist:
			return word["dictionary_form"] == dictionary_form

	def matches(self, wordlist, glob):
		regex = re.compile(fnmatch.translate(glob))
		for word in wordlist:
			for form in self.searchable_forms:
				conj = self.get_form(word, form)
				if conj is not None and regex.match(conj):
					yield word #or put it in list and return
					break

	def search(self, glob):
		if not self.wordlist:
			print("Error: Wordlist is empty")
		if not self.searchable_forms:
			print("Error: Seachable Forms is empty")
		return list(self.matches(self.wordlist, glob))
	#end helper functions for the editmode class

#class WordlistEntry:
def wordlist_entry(dictionary_form, conjugation, part_of_speech = None, meaning = None):
	r = {}
	r["dictionary_form"] = dictionary_form
	r["conjugation"] = conjugation
	r["part_of_speech"] = part_of_speech
	r["meaning"] = meaning
	return r
