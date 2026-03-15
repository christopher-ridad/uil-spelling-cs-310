import logging
import requests
import sys


sys.tracebacklimit = 0

baseurl = "https://qk7g2mpk1h.execute-api.us-east-1.amazonaws.com/test"

def stats_client (userId):
    try:
        url = baseurl + "/stats" + f"/{userId}"

        print(f"Calling web service to stats with userId '{userId}'...")

        response = requests.get(url)

        if response.status_code != 200:

            print("**ERROR: failed with status code:", response.status_code)

            if response.status_code == 500 or response.status_code == 400:
                body = response.json()
                print("**Message:", body["message"])

            sys.exit(0)

        body = response.json()

        streak = body["data"]["streak"]

        total_practiced = body["data"]["totalPracticed"]

        accuracy = body["data"]["accuracy"]

        time_series = body["data"]["daily"]

        print(f"Current Streak: {streak}\n")
        print(f"Total Number of Words Practiced: {total_practiced}\n")
        print(f"Current Accuracy: {accuracy}\n")
        print(f"Time Series of Words Practiced:\n")

        for day, count in time_series.items():
            print(f"\tTotal Words Practiced On {day}: {count}\n")
    
    except Exception as err:
        logging.error("stats_client():")
        logging.error(str(err))
        raise


if __name__ == "__main__":
    stats_client(61)