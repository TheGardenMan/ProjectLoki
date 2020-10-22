import psycopg2
# While running this file separately,below import will cause error.But with django,it won't.Do DNW
# ToDo:insert to append in all files
from . import s3_handle
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
		cursor.execute("select req_receiver_id from follow_requests where req_sender_id=%s",(sender_id,))
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
	# Return people I follow
	try:
		cursor.execute(" select followee_id from followers where follower_id=%s",(follower_id,))
		followee_ids=cursor.fetchall()
		followee_ids=[r[0] for r in followee_ids]
		return followee_ids
	except Exception as e:
		print("Error at followees ",e)
		return 0

def accepted_follow_requests(req_acceptee_id,bottom_flag=0):
	# Send 5 results at a time.Return 0 when there's no result.Front-end takes care of collisions
	try:
		if bottom_flag:
			cursor.execute("select req_acceptor_id,accept_id from follow_requests_accepted where req_acceptee_id=%s and accept_id<%s order by accept_time desc limit 5;",(req_acceptee_id,bottom_flag,))
		else:
			cursor.execute("select req_acceptor_id,accept_id from follow_requests_accepted where req_acceptee_id=%s order by accept_time desc limit 5;",(req_acceptee_id,))

		acceptee_ids=cursor.fetchall()
		bottom_flag=0
		if len(acceptee_ids)>0:
			# Select the last accept_id as bottom_flag
			bottom_flag=acceptee_ids[len(acceptee_ids)-1][1]
			acceptee_ids=[r[0] for r in acceptee_ids]
			result={'acceptee_ids':acceptee_ids,'bottom_flag':bottom_flag}
			print(result)
			return result
		return 0
	except Exception as e:
		print("Error at accepted_follow_requests ",e)
		return 0

def follow_requests_received(req_receiver_id):
	cursor.execute("select req_sender_id from follow_requests where req_receiver_id=%s order by req_time desc;",(req_receiver_id,))
	req_sender_ids=cursor.fetchall()
	req_sender_ids=[r[0] for r in req_sender_ids]
	if len(req_sender_ids)>0:
		return req_sender_ids
	return 0

# receiver is current user.sender is some guy.
def delete_received_follow_request(req_receiver_id,req_sender_id):
	try:
		cursor.execute("delete from follow_requests where req_sender_id=%s and req_receiver_id=%s;",(req_sender_id,req_receiver_id,))
		connection.commit()
		return 1
	except Exception as e:
		print("Error at delete_received_follow_request",e)
		return 0

def delete_follower(followee_id,follower_id):
	try:
		cursor.execute("delete from followers where followee_id=%s and follower_id=%s;",(followee_id,follower_id,))
		connection.commit()
		return 1
	except Exception as e:
		print("Error at delete_follower ",e)
		return 0

def followers(followee_id):
	try:
		cursor.execute("select follower_id from followers where followee_id=%s",(followee_id,))
		followee_ids=cursor.fetchall()
		if len(followee_ids)>0:
			followee_ids=[r[0] for r in followee_ids]
			return followee_ids
		return 0
	except Exception as e:
		print("Error at followers ",e)
		return 0

def update_user_location(user_id,longitude,latitude):
	try:
		# Do not commit inside a procedure when using psycopg2.Do not inside the statement either.. Use connection.commit() only
		cursor.execute("call update_user_location(%s,%s,%s);",(user_id,longitude,latitude,))
		connection.commit();
		return 1
	except Exception as e:
		print("Error at update_user_location ",e)
		return 0

def find_nearby_people(user_id):
	try:
		cursor.execute("select user_id from user_last_location where ST_DWithin(last_location,(select last_location from user_last_location where user_id=%s),5000) and user_id NOT IN(select followee_id from followers where follower_id=%s) order by last_time desc limit 10;",(user_id,user_id,))
		people=cursor.fetchall()
		people=[p[0] for p in people]
		# user_id is incld in it.so..
		people.remove(user_id)
		if len(people)==0:
			return 0
		return people
	except Exception as e:
		print("Error at find_nearby_people ",e)
		return 0

def follow_status(user_A,user_B):
	try:
		cursor.execute("select \"follow_status\"(%s,%s);",(user_A,user_B,))
		status=cursor.fetchone()
		return status[0]
	except Exception as e:
		print("Error at follow_status ",e)
		return 0
# This is Ramanan's first commit.When we return id's from various APIs,front-end calls this API to get username of that
def get_username(user_id):
	try:
		cursor.execute("select username from auth_user where id = %s;",(user_id,))
		req_username = cursor.fetchone()
		return req_username[0]
	except Exception as e:
		print("Error at get_username ",e)
		return 0

def like_private_post(user_id,post_id):
	try:
		cursor.execute("update private_posts set likes = likes+1 where user_id = %s and private_post_id = %s;",(user_id,post_id,))
		connection.commit()
		return 1
	except Exception as e:
		print("Error at like_private_post",e)
		return 0

def unlike_private_post(user_id,post_id):
	try:
		cursor.execute("update private_posts set likes = likes-1 where user_id = %s and private_post_id = %s and likes>0;",(user_id,post_id,))
		connection.commit()
		return 1
	except Exception as e:
		print("Error at unlike_private_post",e)
		return 0

def private_posts(user_id):
	try:
		cursor.execute("select private_post_id, views, likes from private_posts where user_id = %s order by private_post_time desc;",(user_id,))
		post_details = cursor.fetchall()
		if len(post_details)>0:
			return post_details
		return 0
	except Exception as e:
		print("Error at private_posts",e)
		return 0

def delete_private_post(private_post_id):
	try:
		cursor.execute("update private_posts set deleted = 1 where private_post_id = %s;",(private_post_id,))
		connection.commit()
		return 1
	except Exception as e:
		print("Error at delete_private_post",e)
		return 0

def search(username):
	try:
		cursor.execute("select id from auth_user where username like '%{0}%';".format(username))
		results = cursor.fetchall()
		results = [r[0] for r in results]
		if len(results)>0:
			return results
		return 0
	except Exception as e:
		print("Error at search",e)
		return 0
		
# LW
def get_new_public_post_id(user_id):
	try: 
		cursor.execute("select max(public_post_id) from public_posts where user_id=%s;",(user_id,))
		new_post_id=cursor.fetchone()
		if new_post_id[0]:
			return int(new_post_id[0])+1
			# If first post
		return 1
	except Exception as e:
		print(" Error at get_new_public_post_id ",e)
		return 0

def public_post_success(user_id,public_post_id,longitude,latitude):
	try:
		cursor.execute('''
			insert into public_posts(user_id,public_post_id,public_post_location,public_post_time,views,likes,dislikes,deleted) 
			values(%s,%s,ST_MakePoint(%s,%s),current_timestamp,0,0,0,false);''',(user_id,public_post_id,longitude,latitude,)
			)
		connection.commit()
		return 1
	except Exception as e:
		print("Error at public_post_success ",e)
		return 0

def get_new_private_post_id(user_id):
	try: 
		cursor.execute("select max(private_post_id) from private_posts where user_id=%s;",(user_id,))
		new_post_id=cursor.fetchone()
		if new_post_id[0]:
			return int(new_post_id[0])+1
			# If first post
		return 1
	except Exception as e:
		print(" Error at get_new_private_post_id ",e)
		return 0

def private_post_success(user_id,private_post_id):
	try:
		cursor.execute("insert into private_posts(user_id,private_post_id,private_post_time,views,likes,deleted) values(%s,%s,current_timestamp,0,0,false);",(user_id,private_post_id,))
		connection.commit()
		return 1
	except Exception as e:
		print(" Error at private_post_success ",e)
		return 0

def public_feed(user_id,lastpost_user_id=None,lastpost_post_id=None):
	if not lastpost_user_id:
		cursor.execute("select public_feed_first_request(%s);",(user_id,))
	else:
		cursor.execute("select public_feed_subsequent_request(%s,%s,%s);",(user_id,lastpost_user_id,lastpost_post_id,))
	# cursor.fetchall() format : [('(122,4,0,0,0)',), ('(122,3,0,0,0)',), ('(122,2,0,0,0)',)]
	results=[]
	for index,row in enumerate(cursor.fetchall()):
		# row format ('(122,4,0,0,0)',)
		# row[0] format (122,4,0,0,0). Type 'str'.I know it sucks.
		# remove that parantheses. OPTIMIZE the replace
		temp_row=row[0].replace("(","")
		temp_row=temp_row.replace(")","")
		cleaned_row=temp_row.split(",")
		# cleaned_row ['122', '2', '0', '0', '0'] ['user_id','public_post_id','views','likes','dislikes']
		# Get the s3 URL
		cleaned_row.insert(5,s3_handle.get_download_url(''.join(['public_',cleaned_row[0],'_',cleaned_row[1],'.jpg'])))
		results.insert(index,cleaned_row)
		# Changed:return was inside the loop
	return results

def public_post_action(user_id,public_post_id,action):
	try:
		cursor.execute("call public_post_actions(%s,%s,%s);",(user_id_,public_post_id,action,))
		connection.commit()
		return 1
	except Exception as e:
		print(" Error at public_post_action ",e)
		return 0

def delete_file(user_id,public_post_id):
	try:
		cursor.execute("update public_post set deleted=true where user_id=%s and public_post_id=%s;",(user_id,public_post_id,))
		connection.commit()
		result=s3_handle.delete_file(''.join ( ["public_",user_id,"_",public_post_id] ) )	
		return result
	except Exception as e:
		print("Error at db_handle.delete_file ",e)
		return 0

def public_posts(user_id):
	try:
		cursor.execute("select user_id,public_post_id,views,likes,dislikes from public_posts where user_id=%s order by public_post_time desc;",(user_id,))
		results=cursor.fetchall() # [(121,1,2,2,2),(121,2,2,2,2)]....
		post_details=[]

		for detail in results:
			temp=[i for i in detail]
			# Changed:Added S3 download URLs
			filename=''.join(['public_',str(detail[0]),'_',str(detail[1]),'.jpg'])
			# append 
			temp.append(s3_handle.get_download_url(filename))
			post_details.append(temp)
		return post_details
	except Exception as e:
		print("Error at public_posts ",e)
		return 0

def new_public_post_check(user_id,public_post_id):
	try:
		cursor.execute("select new_public_post_check(%s,%s);",(user_id,public_post_id,))
		# [(3,)] or [(None,)]
		if (cursor.fetchall()[0][0])==None:
			return 0
		return 1
	except Exception as e:
		print("Error at new_public_post_check ",e)
		# ToDo -1?!
		return -1
