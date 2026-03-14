import random
from datetime import datetime, timedelta
import pymysql
import logging

from configparser import ConfigParser
from tenacity import retry, stop_after_attempt, wait_exponential


SPELLINGAPP_CONFIG_FILE = "../spellingapp-config.ini"
TWO_MONTHS = 60 * 60 * 24 * 60


def get_dbConn():
    try:
        configur = ConfigParser()
        configur.read(SPELLINGAPP_CONFIG_FILE)

        endpoint = configur.get('rds', 'endpoint')
        portnum = int(configur.get('rds', 'port_number'))
        username = configur.get('rds', 'user_name')
        pwd = configur.get('rds', 'user_pwd')
        dbname = configur.get('rds', 'db_name')

        dbConn = pymysql.connect(
            host=endpoint,
            port=portnum,
            user=username,
            password=pwd,
            database=dbname,
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
        )

        return dbConn
    
    except Exception as err:
        logging.error("get_dbconn():")
        logging.error(str(err))
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
def add_users(userfile):
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()

        dbConn.begin()

        with open(userfile, "r") as file:
            for line in file:
                username = line.strip()

                sql = """
                    INSERT INTO users (username)
                    VALUES (%s);
                """

                dbCursor.execute(sql, (username,))
        
        dbConn.commit()
            
    except Exception as err:
        dbConn.rollback()

        logging.error("add_users():")
        logging.error(str(err))
        raise

    finally:
        try: 
            dbCursor.close()
        except: 
            pass
        try:
            dbConn.close()
        except:
            pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
def add_words(wordfile):
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()

        dbConn.begin()

        with open(wordfile, "r") as file:
            for line in file:
                word = line.strip()
                
                sql = """
                    INSERT INTO words (word)
                    VALUES (%s);
                """

                dbCursor.execute(sql, (word,))
        
        dbConn.commit()
            
    except Exception as err:
        dbConn.rollback()

        logging.error("add_words():")
        logging.error(str(err))
        raise

    finally:
        try: 
            dbCursor.close()
        except: 
            pass
        try:
            dbConn.close()
        except:
            pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
def add_history():
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()

        seen_pairs = set([(None, None)])

        dbConn.begin()

        for _ in range(1_000):
            userId = None
            wordId = None

            while (userId, wordId) in seen_pairs:
                userId = random.randint(1, 100)
                wordId = random.randint(1, 1500)

            seen_pairs.add((userId, wordId))

            totalAttempts = max(int(random.gauss(25, 25)), 0)
            correct = min(max(int(random.gauss(15, 15)), 0), totalAttempts)

            now = datetime.now()

            created_seconds = random.randint(0, TWO_MONTHS)
            created_timestamp = now - timedelta(seconds=created_seconds)

            last_seen_seconds = random.randint(0, created_seconds)
            last_seen_timestamp = now - timedelta(seconds=last_seen_seconds)

            created_at = created_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            last_seen = last_seen_timestamp.strftime("%Y-%m-%d %H:%M:%S")

            sql = """
                INSERT INTO user_history(
                    user_id, 
                    word_id, 
                    correct, 
                    total_attempts, 
                    last_seen, 
                    created_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                ); 
            """

            dbCursor.execute(sql, (
                userId,
                wordId,
                correct,
                totalAttempts,
                last_seen,
                created_at
            ))

        dbConn.commit()
    
    except Exception as err:
        dbConn.rollback()

        logging.error("add_history():")
        logging.error(str(err))
        raise

    finally:
        try: 
            dbCursor.close()
        except: 
            pass
        try:
            dbConn.close()
        except:
            pass


if __name__ == "__main__":
    add_users("users.txt")
    add_words("words.txt")
    add_history()
