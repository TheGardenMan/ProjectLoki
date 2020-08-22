import psycopg2
isError=False
cursor="blah"

try:
	connection = psycopg2.connect(user = "postgres",
								  password = "jaxtek",
								  host = "127.0.0.1",
								  port = "5432",
								  database = "postgres")
	cursor = connection.cursor()

except (Exception, psycopg2.Error) as error :
	print ("Error while connecting to PostgreSQL", error)
	isError=True

def username_check(username):
	cursor.execute("select count(username) from auth_user where username=%s",(username,))
	count=cursor.fetchone()
	count=f"{count[0]}"
	# Assuming there's maximum one username
	if count=="0":
		return 1 #Available
	return 0 #Not available