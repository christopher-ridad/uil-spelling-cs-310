The layer zip file and the lambda function file are both zipped within this folder.

You should be able to upload these to lambda relatively easily to create the function.

However, you will have to define FIVE environmental variables:


** EnvVar Key **           ** EnvVar Value **

   DB_NAME                    spellingapp

   ENDPOINT                   mysql-nu-cs310.crmi4kcy0d99.us-east-2.rds.amazonaws.com

   PORT_NUMBER                3306

   USER_NAME                  app_user

   USER_PWD                   password123


Other (potentially) helpful information: 

The API endpoint is /stats/{userId}

The database is connected via the code in build_rds (no need to connect it on your side)


Thank you for all of your hard work Chris! 🫶