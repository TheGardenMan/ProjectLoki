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

def follow(req_sender_id,req_receiver_id):
	try:
		cursor.execute("insert into follow_requests(req_sender_id,req_receiver_id,req_time) values(%s,%s,current_timestamp);",(req_sender_id,req_receiver_id))
		connection.commit()
		return 1
	except Exception as e:
		# ToDo what to do if he tries to follow a guy he already follows.
		print("Error at follow in db_handle ",e)
		return 0

def accept_follow_request(follower_id,followee_id):
	# follower_id=req_sender_id=req_acceptee_id
	# followee_id=req_receiver_id=req_acceptor_id
	try:
		cursor.execute('''
			begin;
			delete from follow_requests where req_sender_id=%s and req_receiver_id=%s;
			insert into follow_requests_accepted(req_acceptor_id,req_acceptee_id,accept_time) values(%s,%s,current_timestamp);
			insert into followers(follower_id,followee_id) values(%s,%s);
			end transaction;
			'''
			,(follower_id,followee_id,followee_id,follower_id,follower_id,followee_id,))
		# no need to commit since "end transaction" means "commit"
		return 1
	except Exception as e:
		print("Error at accept_follow_request ",e)
		return 0
	else:
		return 1

def unfollow(unfollower_id,unfollowee_id):
	try:
		cursor.execute(" delete from followers where follower_id=%s and followee_id=%s;",(unfollower_id,unfollowee_id))
		connection.commit();
		return 1
	except Exception as e:
		print("Error at unfollow ",e)
		return 0

def follow_requests_sent(sender_id):
	try:
		cursor.execute("select req_sender_id from follow_requests where req_sender_id=%s",(sender_id,))
		request_ids=cursor.fetchall()
		request_ids=[r[0] for r in request_ids]
		return request_ids
	except Exception as e:
		return 0

def delete_sent_follow_request(req_sender_id,req_receiver_id):
	try:
		cursor.execute("delete from follow_requests where req_sender_id=%s and req_receiver_id=%s;",(req_sender_id,req_receiver_id,))
		connection.commit();
		return 1
	except Exception as e:
		print("Error at delete_sent_follow_request ",e)
		return 0

def followees(follower_id):
	try:
		cursor.execute(" select followee_id from followers where follower_id=%s",(follower_id,))
		followee_ids=cursor.fetchall()
		followee_ids=[r[0] for r in followee_ids]
		return followee_ids
	except Exception as e:
		print("Error at followees ",e)
		return 0

def accepted_follow_requests(req_acceptee_id,bottom_flag=0):
	try:
		if bottom_flag:
			cursor.execute("select req_acceptor_id,accept_id from follow_requests_accepted where req_acceptee_id=%s and accept_id<%s order by accept_time desc limit 5;",(req_acceptee_id,bottom_flag,))
		else:
			cursor.execute("select req_acceptor_id,accept_id from follow_requests_accepted where req_acceptee_id=%s order by accept_time desc limit 5;",(req_acceptee_id,))

		acceptee_ids=cursor.fetchall()
		acceptee_ids=[r[0] for r in acceptee_ids]
		# LastW return acceptee_ids and pointer(i.e accept_id) for last of acceptee_ids (return as 2 separate variabls).Dont send all accept_ids..
		# If no results or error,handle accordingly.
		print(acceptee_ids)
		return 0
	except Exception as e:
		print("Error at accepted_follow_requests ",e)
		return 0
