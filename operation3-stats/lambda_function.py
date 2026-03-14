import json
import inspect
import logging
import pymysql

from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, timedelta

from build_rds import data_to_rds as rds


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
def check_user(userId):
    try:
        dbConn = rds.get_dbConn()
        dbCursor = dbConn.cursor()

        sql = """
            SELECT
            username
            FROM users
            WHERE user_id = %s;
        """
            
        dbCursor.execute(sql, (userId,))
        row = dbCursor.fetchone()

        if not row:
            raise ValueError("no such userId exists")
        
    except Exception as err:
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name

        logging.error(f"{caller_name}.check_user():")
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
def get_streak(userId):
    try:
        dbConn = rds.get_dbConn()
        dbCursor = dbConn.cursor()

        check_user(userId)

        sql = """
            SELECT
            DATEDIFF(CURDATE(), DATE(last_seen))
            FROM user_history
            WHERE user_id = %s;
        """
            
        dbCursor.execute(sql, (userId,))
        rows = dbCursor.fetchall()

        seen_days = {int(row[0]) for row in rows}

        streak = 0
        while streak in seen_days:
            streak += 1
        
        return streak
        
    except Exception as err:
        logging.error("lambda_handler.get_streak():")
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
def get_totalPracticed(userId):
    try:
        dbConn = rds.get_dbConn()
        dbCursor = dbConn.cursor()

        check_user(userId)

        sql = """
            SELECT
            COALESCE(SUM(total_attempts > 0), 0)
            FROM user_history
            WHERE user_id = %s;
        """
            
        dbCursor.execute(sql, (userId,))
        row = dbCursor.fetchone()

        return int(row[0])
        
    except Exception as err:
        logging.error("lambda_handler.get_totalPracticed():")
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
def get_accuracy(userId):
    try:
        dbConn = rds.get_dbConn()
        dbCursor = dbConn.cursor()

        check_user(userId)

        sql = """
            SELECT
            COALESCE((SUM(correct) / NULLIF(SUM(total_attempts),0)) * 100, 0)
            FROM user_history
            WHERE user_id = %s;
        """
            
        dbCursor.execute(sql, (userId,))
        row = dbCursor.fetchone()

        return int(row[0])
        
    except Exception as err:
        logging.error("lambda_handler.get_accuracy():")
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
def get_daily(userId):
    try:
        dbConn = rds.get_dbConn()
        dbCursor = dbConn.cursor()

        sql = """
            SELECT
            DATE(last_seen), COUNT(*)
            FROM user_history
            WHERE user_id = %s
            GROUP BY DATE(last_seen)
            ORDER BY DATE(last_seen) DESC;
        """
            
        dbCursor.execute(sql, (userId,))
        rows = dbCursor.fetchall()
        data = {}

        for row in rows:
            data[str(row[0])] = int(row[1])
        
        return data
        
    except Exception as err:
        logging.error(f"lambda_handler.get_daily():")
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


def lambda_handler(event, context):
    try:
        print("**Call to stats...")

        print("**Accessing request pathParameters")

        if "pathParameters" not in event or event["pathParameters"] is None:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": "request has no pathParameters", "data": {}})
            }

        path_params = event["pathParameters"]

        if "userId" not in path_params:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": "request has no key 'userId'", "data": {}})
            }

        userId = int(path_params["userId"])

        print("userId:", userId)

        print("**Generating stats...")

        streak = get_streak(userId)

        totalPracticed = get_totalPracticed(userId)

        accuracy = get_accuracy(userId)

        daily = get_daily(userId)

        print("**Responding to client...")

        body = {
            "message": "success",
            "data": {
                "streak": streak,
                "totalPracticed": totalPracticed,
                "accuracy": accuracy,
                "daily": daily
            }
        }

        return {
            'statusCode': 200,
            'body': json.dumps(body)
        }

    except Exception as e:
        
        print("**Exception")
        print("**Message:", str(e))

        body = {
            "message": str(e),
            "data": {}
        }

        if str(e) == "no such userId exists":
            return {
                'statusCode': 400,
                'body': json.dumps(body)
            }

        return {
            'statusCode': 500,
            'body': json.dumps(body)
        }