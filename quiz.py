#
# Client-side app to run a UIL spelling quiz.
#
# The app calls the following endpoints:
#   1. POST /quiz to get a list of words to practice
#   2. POST /misspell (4 times per word) to get wrong answer choices
#   3. GET /stats/{userId} to show performance at the end
#
import requests
import sys
import random

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

baseurl = "https://qk7g2mpk1h.execute-api.us-east-1.amazonaws.com/test"

#
# helper functions to call each endpoint:
#

def get_quiz_words(user_id, count):
  url = baseurl + "/quiz"
  response = requests.post(url, json={"userId": user_id, "count": count})
  if response.status_code != 200:
    print("**ERROR: failed to get quiz words:", response.status_code)
    sys.exit(0)
  return response.json()["data"]["words"]

def get_misspelling(word):
  url = baseurl + "/misspell"
  response = requests.post(url, json={"word": word})
  if response.status_code != 200:
    print("**ERROR: failed to get misspelling:", response.status_code)
    sys.exit(0)
  return response.json()["data"]["misspelling"]

def get_stats(user_id):
  url = baseurl + f"/stats/{user_id}"
  response = requests.get(url)
  if response.status_code != 200:
    print("**ERROR: failed to get stats:", response.status_code)
    sys.exit(0)
  return response.json()["data"]

#
# main quiz loop:
#

print("Welcome to the UIL Spelling Quiz!")
print("----------------------------------")

user_id = input("Enter your user ID: ")
num_words = 5  # number of words per quiz session

print(f"\nFetching {num_words} words for your quiz...")
words = get_quiz_words(user_id, num_words)

correct_count = 0

for i, word in enumerate(words):
  print(f"\nQuestion {i + 1} of {num_words}")
  print("Which of the following is spelled correctly?")

  #
  # get 4 misspellings of this word, then combine
  # with the correct spelling and shuffle:
  #
  print("Generating answer choices...")
  misspellings = []
  attempts = 0

  while len(misspellings) < 4 and attempts < 8:
    m = get_misspelling(word)
    # make sure we don't get duplicates or the correct word back:
    if m not in misspellings and m != word:
      misspellings.append(m)
    attempts += 1

  choices = misspellings + [word]
  random.shuffle(choices)

  #
  # display the choices:
  #
  for j, choice in enumerate(choices):
    print(f"  {j + 1}. {choice}")

  #
  # get the user's answer:
  #
  while True:
    answer = input("Your answer (1-5): ")
    if answer.isdigit() and 1 <= int(answer) <= 5:
      break
    print("Please enter a number between 1 and 5.")

  selected = choices[int(answer) - 1]

  if selected == word:
    print("Correct!")
    correct_count += 1
  else:
    print(f"Wrong! The correct spelling is: {word}")

#
# quiz complete, show results:
#
print("\n----------------------------------")
print(f"Quiz complete! You got {correct_count} out of {num_words} correct.")

#
# fetch and display stats:
#
print("\nFetching your overall stats...")
stats = get_stats(user_id)

print(f"Current streak:    {stats['streak']} days")
print(f"Total practiced:   {stats['totalPracticed']} words")
print(f"Overall accuracy:  {int(stats['accuracy'] * 100)}%")