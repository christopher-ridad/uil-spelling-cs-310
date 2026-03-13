#
# Client-side app to input a word and send it to the misspell
# web service, which returns a single plausible misspelling.
#
import requests
import sys

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0


baseurl = "https://qk7g2mpk1h.execute-api.us-east-1.amazonaws.com/test"

url = baseurl + "/misspell"

word = input("Word to misspell? ")

data = {
  "word": word
}

print(f"Calling web service to misspell '{word}'...")

response = requests.post(url, json=data)

#
# what did we get back?
#
if response.status_code != 200:
  # failed:
  print("**ERROR: failed with status code:", response.status_code)
  #
  if response.status_code == 500:  # we'll have an error message
    body = response.json()
    print("**Message:", body["message"])
  #
  sys.exit(0)

#
# deserialize and extract results:
#
body = response.json()

misspelling = body["data"]["misspelling"]

print(f"Misspelling of '{word}': {misspelling}")