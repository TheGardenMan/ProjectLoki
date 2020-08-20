-- Follow Requests
create table follow_requests (req_sender_id integer,req_receiver_id integer,req_time timestamptz);
insert into follow_requests(req_sender_id,req_receiver_id,req_time) values(1,2,current_timestamp);
-- ToDo while returning,also return whether_i_am_following_the_user_who_sent_me_the_follow_request (It's available as a separeat function.I wrote it)
-- Follow requests received by me
select req_sender_id from follow_requests where req_receiver_id=2 order by req_time desc;
-- Follow requests sent by me
select req_sender_id from follow_requests where req_sender_id=1 order by req_time desc;
-- Follow Request accepted by receiver / deleted by sender /deleted by receiver
delete from follow_requests where req_sender_id=1 and req_receiver_id=2;


-- Follow Requests Accepted
create table follow_requests_accepted(req_acceptor_id integer,req_acceptee_id integer,accept_time timestamptz);
insert into follow_requests_accepted(req_acceptor_id,req_acceptee_id,accept_time) values(1,2,current_timestamp);
	-- ToDo are_they_following_me
	-- For notifications:People who accepted my follow requests
select req_acceptor_id from follow_requests_accepted where req_acceptee_id=2 order by accept_time desc;


-- Followers
create table followers(follower_id integer,followee_id integer);
insert into followers(follower_id,followee_id) values(1,2);
	-- My followers
select follower_id from followers where followee_id=2;
	-- People I follow (followees)
select followee_id from followers where follower_id=1;
	-- Unfollow/ Delete my follower
delete from followers where follower_id=1 and followee_id=2;


-- Follow status
	-- Status codes: 1.Not Following 2.Request sent 3.Following
create function return_follow_status(user_A_id integer,user_B_id integer)
  returns integer
as
$$
declare
	follow_status integer;
	temp integer;
begin
	select count(followee_id) into temp from followers where follower_id=user_A_id and followee_id=user_B_id;

	if temp=1 then
		return 3;
	end if;
	select count(req_sender_id) into temp from follow_requests where req_sender_id=user_A_id and req_receiver_id=user_B_id;

	if temp=1 then
		return 2;
	end if;
	return 1;
end;
$$
language plpgsql;

-- Find nearby people
	select user_id from user_last_location where ST_DWithin(last_location, ST_MakePoint(2,3)::geography, 5000) limit 20;

-- Search nearby people
	select user_id from user_last_location where ST_DWithin(last_location, ST_MakePoint(2,3)::geography, 5000) and user_id=(select id from auth_user where username like '%search_query_here%')

-- Last location of user
create table user_last_location(user_id integer,last_location geography);
	-- Check if this is the first insert.If result is 0,insert.Else update
select count(user_id) from user_last_location where user_id=1;
	-- First entry:INSERT
insert into user_last_location(user_id,last_location) values (1,ST_MakePoint(10.1,11.2))
	-- Not first entry:UPDATE
update user_last_location SET last_location=ST_MakePoint(10.1,11.2) where user_id=1;


-- Public posts

-- Table
create table public_posts(user_id integer,public_post_id integer,public_post_location geography,public_post_time timestamptz, views integer,likes integer,dislikes integer,deleted boolean);

-- Make public post :Procedure
-- In $BODY$,"BODY" could be anything
CREATE OR REPLACE PROCEDURE make_public_post(
	user_id_ integer,
	longitude_ integer,
	latitude_ integer
)
LANGUAGE 'plpgsql'
AS $BODY$
declare
	new_post_id integer; 
BEGIN
	select count(public_post_id) into new_post_id from public_posts where user_id=user_id_;
	raise notice ' Old public_post_id for user_id % is %',user_id_,new_post_id;
	new_post_id:=new_post_id+1;
	raise notice ' New public_post_id for user_id % is %',user_id_,new_post_id;
	insert into public_posts(user_id,public_post_id,public_post_location,public_post_time,views,likes,dislikes,deleted) values(user_id_,new_post_id,ST_MakePoint(longitude_,latitude_),current_timestamp,0,0,0,false);
	commit;
	raise notice 'public post created successfully %',user_id_;
END;
$BODY$;
-- call the procedure
call make_public_post(1,2,3);

-- actions 
-- 1.like_increment 2.like_decrement 3.dislike_increment 4.dislike_decrement 5.view_increment
-- caveat:Front-end takes care of whether user has already liked it or not
CREATE OR REPLACE PROCEDURE public_post_actions(user_id_,public_post_id_,action_)
LANGUAGE 'plpgsql'
AS $BODY$
declare
	likes_ integer;
	dislikes_ integer;
	views_ integer;
BEGIN
	select likes,dislikes,views into likes_,dislikes_,views_ from public_posts where user_id=user_id_ and public_post_id=public_post_id_;
	if action_=1 then
		likes_:=likes_+1;
	elsif action_=2 then
		likes_:=likes_-1;
	elsif action_=3 then
		dislikes_:=dislikes_+1;
	elsif action_=4 then
		dislikes_:=dislikes_-1;
	elseif action_=5 then
		views_=views_+1;
	else
		raise exception 'PG:Wrong action number from client';
	end if;
	update public_posts set views=views_,likes=likes_,dislikes=dislikes_ where user_id=user_id_ and public_post_id=public_post_id_;
	commit;
	raise notice 'PG:public action_ % done successfully',action_;
END;
$BODY$;

-- my_public_posts
select user_id,public_post_id,views,likes,dislikes from public_posts where user_id=1 order by public_post_time desc;

-- delete public post
update public_posts set deleted=true where user_id=1 and public_post_id=1;

-- public_feed
-- First request
	SELECT user_id,public_post_id,views,likes,dislikes FROM public_posts WHERE ST_DWithin(public_post_location, ST_MakePoint(2,3)::geography, 5000) order by public_post_time desc limit 20;
-- Subsequent requests
	-- Find the timestamp using pointer (last_seen_post=>(user_id,public_post_id))
	select public_post_time from public_posts where public_post_id=1 and user_id=2;

	-- Find nearby posts "Older" than the timestamp found above
	SELECT user_id,public_post_id,views,likes,dislikes FROM public_posts WHERE ST_DWithin(public_post_location, ST_MakePoint(2,3)::geography, 5000) and public_post_time<(select public_post_time from public_posts where user_id=1 and public_post_id=3) order by public_post_time desc limit 20;
	-- Are there new public posts? If result is > 0,AVAILABLE.
	-- Receive "TOP" post id,return count(content) newer than that.If user wish to see the enw content,he can hit refresh.

	select count(public_post_id) from public_posts where ST_DWithin(public_post_location, ST_MakePoint(2,3)::geography, 5000) and public_post_time>(select public_post_time from public_posts where user_id=1 and public_post_id=3);
	-- LW
	-- Return new posts



-- Private posts
	-- Table
	create table private_posts(user_id integer,private_post_id integer,private_post_time timestamptz,views integer,likes integer,deleted boolean);

-- make private post
CREATE OR REPLACE PROCEDURE make_private_post(
	user_id_ integer
)
LANGUAGE 'plpgsql'
AS $BODY$
declare
	new_post_id integer; 
BEGIN
	select count(private_post_id) into new_post_id from private_posts where user_id=user_id_;
	raise notice ' Old private_post_id for user_id % is %',user_id_,new_post_id;
	new_post_id:=new_post_id+1;
	raise notice ' New private_post_id for user_id % is %',user_id_,new_post_id;
	insert into private_posts(user_id,private_post_id,private_post_time,views,likes,deleted) values(user_id_,new_post_id,current_timestamp,0,0,false);
	commit;
	raise notice 'Private post created successfully by %',user_id_;
END;
$BODY$;
call make_private_post(1);

-- 


-- Private post actions
-- 1.like_increment 2.like_decrement 3.view_increment
create or replace procedure private_post_actions(user_id_,private_post_id_,action_)
LANGUAGE 'plpgsql'
AS $BODY$
declare
	likes_ integer;
	views_ integer;
BEGIN
	select likes,views into likes_,views_ from private_posts where user_id=user_id_ and private_post_id=private_post_id_;
	if action_=1 then
		likes_:=likes_+1;
	elsif action_=2 then
		likes_:=likes_-1;
	elseif action_=3 then
		views_=views_+1;
	end if;
	update private_posts set views=views_,likes=likes_ where user_id=user_id_ and private_post_id=private_post_id_;
	commit;
	raise notice 'PG:private action_ % done successfully',action_;
	END;
$BODY$;

-- my_private_posts
	select user_id,private_post_id,views,likes from private_posts where user_id=1 order by private_post_time desc;

-- delete private post
	update private_posts set deleted=true where user_id=1 and private_post_id=1;

-- private feed
	-- First request
	select user_id,private_post_id,views,likes from private_posts where user_id=(select followee_id from followers where follower_id=1) order by private_post_time desc;

-- Subsequent requests using pointer
	-- structure :select detaials from table where user_id=(people I follow) and post_time<(last seen post time)
	select user_id,private_post_id,views,likes from private_posts where user_id=(select followee_id from followers where follower_id=1) and private_post_time<(select private_post_time from private_posts where user_id=1 and private_post_id=2) order by private_post_time desc;
	-- Are there "new" private posts available? IF result is non-zero,AVAILABLE.
	-- Receive "TOP" post id,return count(content) newer than that.If user wish to see the enw content,he can hit refresh.
	select count(private_post_id) from private_posts where user_id=(select followee_id from followers where follower_id=1) and private_post_time>(select private_post_time from private_posts where user_id=1 and private_post_id=2);
-- Users table

-- Username availability check
-- If it returns 0,username is available.Case sensitive
select count(username) from auth_user where username='Al';

-- Change username 
update auth_user set username='Jxxxxxxx' where id=82;

-- Get user name
select username from auth_user where user_id
