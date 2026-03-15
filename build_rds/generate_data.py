import json
import re


def generate_wordfile(output_file):
    with open(output_file, "w") as file:
        file.write("")

    with open("raw_wordlist.json") as file:
        words = json.load(file)

        for word in words:
            pattern = r',\s|\s\('
            word = re.split(pattern, word)

            with open(output_file, "a") as file:
                file.write(f"{word[0].lower()}\n")


if __name__ == "__main__":
    generate_wordfile("words.txt")
