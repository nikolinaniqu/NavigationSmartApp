import random
import datetime as dt
import functools
import json
import time
import string


def nice(atext: str,
         size: int = 60,
         filling: str = ' ',
         border: str = '|',
         top_bottom: str = '-',
         corner: str = '+') -> None:
	"""
	prints default box:\n
	``+-------------+``\n
	``|    txt     |``\n
	``+-------------+``\n
	If ``\\`` n is detected in txt, new lines are added with the same filling and border
	:param atext: - str: txt to be printed in box
	:param size: - int: width of box in number of characters. Default = 60
	:param filling: - str: filling of the box. Default = whitespace
	:param border: - str: left and right border of the box. Default = '|'
	:param top_bottom: - str: top and bottom of the box. Default = '-'
	:param corner: - str: corner of the box. Default = '+'
	:return: - None
	"""
	fill_top_bottom = ((size - 2) * top_bottom)[:(size - 2)]

	if '\n' in atext:
		txt_list = atext.split('\n')
		spaces_l_list = []
		spaces_r_list = []
		for txt in txt_list:
			spaces = size - len(txt) - 2
			spaces_l_list.append(spaces // 2 - 1)
			spaces_r_list.append(spaces - (spaces // 2) - 1)

		print(corner + fill_top_bottom + corner)
		for txt, spac_l, spac_r in zip(txt_list, spaces_l_list, spaces_r_list):
			fill_spaces_l = (spac_l * filling)[:spac_l]
			fill_spaces_r = (spac_r * filling)[:spac_r]
			print(border + fill_spaces_l + ' ' + txt + ' ' + fill_spaces_r + border)
		print(corner + fill_top_bottom + corner + '\n')

	else:
		spaces = size - len(atext) - 2
		spaces_l = spaces // 2 - 1
		spaces_r = spaces - spaces_l - 2

		fill_spaces_l = (spaces_l * filling)[:spaces_l]
		fill_spaces_r = (spaces_r * filling)[:spaces_r]
		print(corner + fill_top_bottom + corner)
		print(border + fill_spaces_l + ' ' + atext + ' ' + fill_spaces_r + border)
		print(corner + fill_top_bottom + corner + '\n')


def pretty_input(prompt: str) -> str:
	"""
	Shows the input more pretty with newline + >>
	Does str.strip() on input
	"""
	return input(f'{prompt}\n>> ').strip()


def find_json() -> list:
	"""
	Finds list of json files in directory
	:return: - list: list of the names of the json files
	"""
	import os
	list_files = os.listdir()
	out = []
	for file in list_files:
		if '.json' in file:
			out.append(file)
	return out


def calc_points(user_answer: dict) -> int:
	"""
	Calculates the number of right, wrong and missing answers
	:param user_answer: dict
	:return: inst: total points
	"""
	num_right = 0
	num_wrong = 0
	no_answer = 0
	for key, value in user_answer.items():
		print(f"{key}: {value['question']} -- {value['answer']} -- {value['correct']}")
		if 'richtig' in value['correct'].lower():
			num_right += 1
		elif 'falsch' in value['correct'].lower():
			num_wrong += 1
		if '' == value['answer']:
			no_answer += 1

	if run_time <= max_time and no_answer == 0:
		points = num_right * 10 + 50
	else:
		points = num_right * 10
	print(f'\nDu hast {num_right} von {num_wrong + num_right} Fragen richtig beantwortet.\n'
	      f'Damit hast du {points} Punkte erreicht!')

	return points


def select_file(list_json: list) -> str:
	"""
	Function to select json file, minus questions.json
	:param list_json: - list: list of json files
	:return: - str: name of the selected file (without .json!)
	"""
	if 'questions.json' in list_json:
		list_json.remove('../questions.json')
	for num, file in enumerate(list_json):
		print(f'\t({num}) - {file[:-5]}')
	while True:
		choice = pretty_input('Welches File möchtest du? Gebe dazu die Nummer ein').strip()
		if choice.isdigit():
			choice = int(choice)
			if choice < len(list_json):
				return list_json[choice][:-5]
			else:
				print('Ungültige Wahl')
		else:
			print('Bitte gebe eine ganze Zahl an')


def save_highscore(file: str, user_output) -> None:
	highscore = open(f'{file}.json', 'r')
	highscore = json.load(highscore)

	if name in highscore.keys():
		highscore[name].append(user_output)
	else:
		highscore[name] = [user_output]
	json.dump(highscore, open(f'{highscore_file}.json', 'w'))
	print('Highscore ist erfolgreich gespeichert!\n')


def show_highscore(name_file: str) -> None:
	"""
	print the highscore
	name:
		buchstabe --> Punkte -- Zeit -- Datum
	:param name_file: str - name of the json file, without ending
	:return: None
	"""
	jsonfile = json.load(open(f'{name_file}.json', 'r'))
	nice('Highscore', top_bottom='~+', size=80)
	for person in jsonfile.keys():
		print(person)
		for score in jsonfile[person]:
			print(
				f'\tBuchstabe: {score["letter"]} -->\tPunkte: {score["Points"]} -- Zeit: {score["Runtime"]} -- Datum: {score["date"]}')
	print()


def choose_question_dict(choice: str) -> dict:
	"""
	Function to choose the questions for the game
	Loads json if answered 'play'
	Creates json, if not existing
	:param choice: - str: play or anything else
	:return: - dict: dict with [key, question]
	"""
	if 'play' not in choice:
		return question_dict()
	else:
		if 'questions.json' in find_json():
			return json.load(open('../questions.json', 'r'))
		else:
			print('\nEs gibt noch keine Fragen! Du musst eigene Fragen erstellen!\n')
			return question_dict()


def question_dict() -> dict:
	"""
	Function to change the dict of questions in the following steps:
		1. read in questions.json and loads to dict and prints key value pairs (if it doesn\'t exist, creates a new one)
		2. ask if adding or removing question
		3. json dump of dict to questions.json
		4. optional repeat
	"""
	checker = True
	while checker:
		if 'questions.json' in find_json():
			questions = json.load(open('../questions.json', 'r'))
			print()
			for key, value in questions.items():
				print(f'{key}: {value}')
			print()
		else:
			questions = {}
			print('\nEs gibt noch keine Fragen, lege neue an!\n')

		choice = numeric_input('Was willst du tun?:\n'
		                       '\t(1) Frage entfernen\n'
		                       '\t(2) Frage hinzufügen',
		                       min_num=1, max_num=2)

		if choice == 1:
			checker = remove_question(questions)
		else:
			checker = add_question(questions)

		json.dump(questions, open('../questions.json', 'w'))
		choice = yes_no_question('Nochmal?')
		if 'nein' in choice:
			return questions


def add_question(questions: dict) -> bool:
	"""
	Function to add question with key and value to the dict
	returns False, if user types in \'stop\'
	:param questions: dict - dict of questions for stadtlandfluss
	:return: bool - True if successfully, False if user types in \'stop\'
	"""
	add_q = pretty_input('Welche Frage soll hinzugefügt werden?').title()
	while True:
		add_key = pretty_input('Welchen key sollte diese Frage bekommen?').lower()
		if ' ' in add_key and len(add_key) > 2:
			print('Das Wort muss minuteness drei Buchstaben haben')
		elif add_key == 'stop':
			return False
		else:
			questions[add_key] = add_q
			print('Erfolgreich hinzugefügt :)')
			return True


def remove_question(questions: dict) -> bool:
	"""
	Function to remove question of dict
	Gives user keys to delete
	returns False, if user types in \'stop\'
	:param questions: dict - dict of questions for stadtlandfluss
	:return: bool - True if successfully, False if user types in \'stop\'
	"""
	list_of_keys = functools.reduce(lambda x, y: '\t' + x + "\n\t" + y, questions.keys())
	while True:
		remove_item = pretty_input(f'Welche Frage möchtest du löschen?\n\t{list_of_keys}').lower()
		if remove_item in questions.keys():
			questions.pop(remove_item)
			return True
		elif remove_item == 'stop':
			return False
		else:
			print('Das ist nicht Teil des Fragenkataloges... nochmal')


def check_punctuation(astring: str) -> bool:
	"""
	Checks if any character in a string is in string.punctuation or a whitespace
	Accepts Underscore!
	:param astring: - str
	:return: - bool: True if no punctuation (except _) in string
	"""
	not_accepted_char = string.punctuation.replace('_', ' ')
	for character in astring:
		if character in not_accepted_char:
			return False
	return True


def numeric_input(prompt: str, max_num: int, min_num: int = 0) -> int:
	"""
	Checks if the pretty input is an integer and is between two numbers (inclusive)
	:param input_text: - str: txt to be shown in prettyInput
	:param max_num: - int: maximal accepted number (inclusive)
	:param min_num: - int: minimal accepted number (inclusive). Default is 0
	:return: - int: The chosen number
	"""
	while True:
		out = pretty_input(prompt)
		if out.isdigit():
			out = int(out)
			if min_num <= out <= max_num:
				return out
			else:
				print(f'Bitte gebe eine Zahl zwischen {min_num} und {max_num} an')
		else:
			print(f'Bitte gebe eine Zahl zwischen {min_num} und {max_num} an')


def yes_no_question(prompt: str) -> str:
	"""
	Checks if answer is ja or nein.
	Disregards capital/small letters and whitespaces/regex
	:param prompt: - str: Question to be asked, (Ja/Nein) will be added automatically
	:return: - str: ja or nein
	"""
	while True:
		answer = pretty_input(f'{prompt} (Ja/Nein)').lower()
		if answer in ('ja', 'nein'):
			return answer
		else:
			print('Bitte gebe ja oder nein ein')


def check_first_letter(answer: str, theletter: str) -> str:
	"""
	Checks if first character of a string is the same, as theletter
	Returns the string Richtig! if correct or Falsch :( if not.
	:param answer: str - string to be checked
	:param theletter: str - a letter in string
	:return: str - String if correct or not
	"""
	if len(answer) > 1:
		if answer[0] == theletter:
			return 'Richtig!'
		else:
			return 'Falsch :('
	else:
		return 'Falsch :('


def split_answer(answer: str) -> list:
	"""
	Splits the string at the whitespace and returns the first
	and second word of the string in a list
	:param answer: str - string to be split
	:return: list - list with [key, answer]
	"""
	out = answer.split(' ')
	if len(out) == 2:
		return list(map(lambda s: s.strip().lower(), out))
	else:
		return ['invalid', 'invalid']


def update_time(start_time: float) -> float:
	"""
	Calculates the time diff in second
	:param start_time: - float: start time
	:return: - float: time since beginning with two digits
	"""
	return round(time.time() - start_time, 2)


name_given = False  # Marker if playername is defined (for rep.)
max_time = 60
highscore_file = 'highscore'
possible_letter = list(string.ascii_lowercase)
game_over = False

while not game_over and len(possible_letter) > 0:
	nice('Willkommen bei\nStadtLandFluss', top_bottom='+~', filling='<|>', size=80)

	print('Um zu Antworten muss zuerst den key eingeben, dann Leerzeichen, dann deine Antwort.')
	print('Wenn du Tippfehler im key hast, wird dieser NICHT akzeptiert und du musst alles erneut eingeben!')
	print('Wenn du Fertig bist tippe ---> Fertig <--- ein!')
	print('Für jede richtige Antwort bekommst du 10 Punkte, für jede falsche bekommst du 0 Punkte.')
	print('Wenn du vor ende der Zeit fertig bist, bekommst du 50 Punkte extra')
	print('Viel Erfolg :)\n')

	if not name_given:
		if yes_no_question(f'Die Standard-Zeit sind {max_time}s. Möchtest du das ändern?') == 'ja':
			new_time = numeric_input('Wie viele Sekunden möchtest du Zeit haben?', min_num=30, max_num=180)

		change_highscore = yes_no_question(
			f'Möchtest du das Highscore File ändern? Aktuell wird {highscore_file}.json verwendet.')
		if change_highscore == 'ja':
			new_highscore = yes_no_question('Soll ein neues File erzeugt werden?')
			if new_highscore == 'ja':
				while True:
					new_name = pretty_input(
						'Wie soll dies heißen? Denk daran, Sonderzeichen außer _ sind nicht erlaubt.')
					if check_punctuation(new_name):
						json.dump({}, open(f'{new_name}.json', 'w'))
						print(f'\n--> Das File {new_name}.json wurde erfolgreich erzeugt! :) <--\n')
						highscore_file = new_name
						break
					else:
						print('Das war nicht zulässig... bitte nochmal')
			else:
				highscore_file = select_file(find_json())

		# choice if questions for game should be changed
		choice = pretty_input(
			'Willst du die Fragen ändern oder direkt starten?\n'
			'\tWenn du spielen willst gebe --> play <--- ein\n'
			'\tWenn du die Fragen ändern willst, geben irgendetwas anderes ein').lower()

		questions = choose_question_dict(choice)

	# Printing the highscore
	show_highscore(highscore_file)

	######################################
	#   Begin of the actuall game        #
	######################################
	letter = random.choice(possible_letter)
	possible_letter.remove(letter)
	nice(f'Dein Buchstabe ist:\n{letter.upper()}', top_bottom='+~')

	start_time = round(time.time(), 2)
	print('---> Deine Zeit startet JETZT! <---\n')
	user_answer = {}
	for key in questions.keys():
		user_answer[key] = {'question': questions[key], 'answer': '', 'correct': 'Falsch :('}  # falsch ist default

	game_over = False
	while not game_over:
		print()
		for key, value in user_answer.items():
			print(f"{key}: {value['question']} -- {value['answer']}")

		user_input = pretty_input('').strip().lower()
		if user_input == 'fertig':
			game_over = True
		else:
			key, answer = split_answer(user_input)
			if key in user_answer.keys():
				user_answer[key]['answer'] = answer
				user_answer[key]['correct'] = check_first_letter(answer, letter)
			else:
				print('invalid key')

		run_time = update_time(start_time)
		print(f'Zeit: {run_time}\n')
		if run_time > max_time:
			game_over = True

	print()

	nice(f'Du hast:\n{int(run_time)}s\n benötigt', top_bottom='+~', size=40)

	# calc. how many wrong, right and missing answers
	points = calc_points(user_answer)

	# crating new name if not rerun
	if not name_given:
		while True:
			name = pretty_input('\nWas ist der Name unter dem dieses Spiel gespeichert werden soll? '
								'(max. 15 Zeichen, keine Leerzeichen oder Sonderzeichen, außer _)')
			if len(name) <= 15 and check_punctuation(name):
				break
			else:
				print(f'Zu lang... deine Angabe hatte {len(name)} Zeichen, '
					  f'es sind aber nur 15 erlaubt oder du hast Leerzeichen oder Sonderzeichen dabei, außer _.')

	save_highscore(highscore_file, {'letter': letter.upper(),
									'Points': points,
									'Runtime': int(run_time),
									'date': str(dt.datetime.now())})

	end = yes_no_question('Willst du nochmal spielen?')

	if end == 'nein':
		game_over = True
	else:
		name_given = True

if len(possible_letter) == 0:
	print()
	nice('WOW! Du hast alle Buchstaben durch! Beeindruckend!',
		 top_bottom='+~', filling='>><<')
	print()

nice('Bye Bye!', top_bottom='+~', filling='#')


