#Readmeeeeeeeeeeeeeeeee: Do not commit inside a procedure while using psycopg2

-- Username availability check
-- If it returns 0,username is available.Case sensitive
select count(username) from auth_user where username='Al';

-- Follow Requests
-- ToDo==>primary key (req_sender_id,req_receiver_id)
create table follow_requests (req_sender_id integer,req_receiver_id integer,req_time timestamptz);
insert into follow_requests(req_sender_id,req_receiver_id,req_time) values(120,122,current_timestamp);
-- ToDo while returning,also return whether_i_am_following_the_user_who_sent_me_the_follow_request (It's available as a separeat function.I wrote it)
-- For notifications:Follow requests received by me
select req_sender_id from follow_requests where req_receiver_id=2 order by req_time desc;
-- Follow requests sent by me
select req_sender_id from follow_requests where req_sender_id=1 order by req_time desc;
-- Follow Request accepted by receiver / deleted by sender /deleted by receiver
delete from follow_requests where req_sender_id=1 and req_receiver_id=2;


-- TRANSACTION == -- accept follow request
begin;
-- delete the follow request
delete from follow_requests where req_sender_id=120 and req_receiver_id=122;
-- add to accepted requests
insert into follow_requests_accepted(req_acceptor_id,req_acceptee_id,accept_time) values(120,122,current_timestamp);
--add to my followers
insert into followers(follower_id,followee_id) values(120,122);
-- it means commit.You can use it too.
end transaction;

-- Follow Requests Accepted
create table follow_requests_accepted(accept_id SERIAL PRIMARY KEY, req_acceptor_id integer,req_acceptee_id integer,accept_time timestamptz);
insert into follow_requests_accepted(req_acceptor_id,req_acceptee_id,accept_time) values(1,2,current_timestamp);
-- first request:Get new accepted_follow_requests for a guy by timestamp desc.Only new should be "Indicated".Client should store the latest accept_id it received to detect collisions.And it should stop sending requests once collision happens.
select req_acceptor_id,accept_id from follow_requests_accepted where req_acceptee_id=121 order by accept_time desc limit 5;
-- Subsequent requests use accept_id received from client to find "Older" notifs.
select req_acceptor_id,accept_id from follow_requests_accepted where req_acceptee_id=121 and accept_id<7 order by accept_time desc limit 5;


-- Followers
-- ToDo==> pkey(follower_id,followee_id) to avoid duplicates
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
create function follow_status(user_A_id integer,user_B_id integer)
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

select "follow_status"(123,121);

-- Find nearby people I dont follow
-- Warn:Query returns user_id too.We remove it in python.Why NOT IN? != should be used only when subquery returns one row or result
select user_id from user_last_location where ST_DWithin(last_location,(select last_location from user_last_location where user_id=123),5000) and user_id  NOT IN(select followee_id from followers where follower_id=123) order by last_time desc limit 10;

-- Last location of user
create table user_last_location(user_id integer,last_location geography,last_time timestamptz);
	-- Check if this is the first insert.If result is 0,insert.Else update
select count(user_id) from user_last_location where user_id=1;

-- Update user location
-- do not commit inside a procedure while using pycopg2
CREATE OR REPLACE PROCEDURE update_user_location(
	user_id_ integer,longitude_ float(3),latitude_ float(3)
)
LANGUAGE 'plpgsql'
AS $BODY$
declare
	useless_ integer; 
BEGIN
	if exists (select user_id from user_last_location where user_id=user_id_) then
		update user_last_location SET last_location=ST_MakePoint(longitude_,latitude_), last_time=current_timestamp where user_id=1;
	else
		insert into user_last_location(user_id,last_location,last_time) values (user_id_,ST_MakePoint(longitude_,latitude_),current_timestamp);
	end if;
END;
$BODY$;

call update_user_location(121,10.1,11.2);

--------DONE Aug23---------

-- Public posts

-- Table
create table public_posts(user_id integer,public_post_id integer,public_post_location geography,public_post_time timestamptz, views integer,likes integer,dislikes integer,deleted boolean,PRIMARY KEY(user_id,public_post_id));

-- For public post request.
-- why max instead of count? Coz we may delete the last post which may cause confusions.DND
select max(public_post_id) from public_posts where user_id='1';
-- return result +1

-- Make a public post once client confirms.
insert into public_posts(user_id,public_post_id,public_post_location,public_post_time,views,likes,dislikes,deleted) values(122,2,ST_MakePoint(1,2),current_timestamp,0,0,0,false);
-- LW
-- actions 
-- 1.like_increment 2.like_decrement 3.dislike_increment 4.dislike_decrement 5.view_increment
-- caveat:Front-end takes care of whether user has already liked it or not
CREATE OR REPLACE PROCEDURE public_post_actions(user_id_ integer,public_post_id_ integer,action_ integer)
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
	-- Do not commit inside a procedure while psycopg.. Use connection.commit()
	raise notice 'PG:public action_ % done successfully',action_;
END;
$BODY$;

call public_post_actions(1,2,3);
-- my_public_posts
select user_id,public_post_id,views,likes,dislikes from public_posts where user_id=1 order by public_post_time desc;

-- delete public post
-- deleted flag is needed.Coz if we dont have that and delete the latest post user made,max(public_post_id)+1 will return id of the "latest post (which we deleted)".This will cause confusion.Two diff images with same_ids at updated and un_updated clients.
update public_posts set deleted=true where user_id=1 and public_post_id=1;
-- longitude,latitude,old_public_post_id,old_user_id


-- public_feed

		-- First request
		create or replace function public_feed_first_request(post_req_sender_id integer)
		  returns table (user_id_ integer,public_post_id_ integer,views_ integer,likes_ integer,dislikes_ integer)
		as
		$$
		declare
			last_location_ geography;
		begin
			select last_location into last_location_ from user_last_location where user_id=post_req_sender_id;
			return query select user_id,public_post_id,views,likes,dislikes from public_posts WHERE ST_DWithin(public_post_location,last_location_, 5000) and deleted=false order by public_post_time desc limit 2;
		end;
		$$
		language plpgsql;
		commit;
		-- call the func
		select public_feed_first_request(121);


-- Subsequent requests
			create or replace function public_feed_subsequent_request(post_req_sender_id integer,user_id_of_last_post integer,post_id_of_last_post integer)
			  returns table (user_id_ integer,public_post_id_ integer,views_ integer,likes_ integer,dislikes_ integer)
			as
			$$
			declare
				last_location_ geography;
				last_post_timestamp timestamptz;
			begin
				select last_location into last_location_ from user_last_location where user_id=post_req_sender_id;
				select public_post_time  into last_post_timestamp from public_posts where user_id=user_id_of_last_post and public_post_id=post_id_of_last_post;
				return query SELECT user_id,public_post_id,views,likes,dislikes FROM public_posts WHERE ST_DWithin(public_post_location,last_location_, 5000) and public_post_time<(last_post_timestamp) and deleted=false order by public_post_time desc limit 2;
			end;
			$$
			language plpgsql;

		select public_feed_subsequent_request(121,122,2);

	-- Are there new public posts? If result is > 0,AVAILABLE.
	-- Receive "TOP" post id,return count(content) newer than that.If user wish to see the new content,he can hit refresh.
	-- new_post_check
	create or replace function new_public_post_check(user_id_ integer,public_post_id_ integer)
	returns integer
	as
	$$
	declare
		last_location_ geography;
		last_post_timestamp_ timestamptz;
		count_ integer;
	begin
		count_:=0;
		select last_location into last_location_ from user_last_location where user_id=user_id_;
		select  public_post_time into last_post_timestamp_ from public_posts where user_id=user_id_ and public_post_id=public_post_id_;
		-- It's enough if one row exists.No need to count everything.If result contains any content,new_posts are available.
		select public_post_id into count_ from public_posts where ST_DWithin(public_post_location, last_location_,5000) and public_post_time>(last_post_timestamp_) limit 1;
		return count_;
	end;
	$$
	language plpgsql;
	commit;
	-- if len(res)>0:
		-- return 1
	select new_public_post_check(122,5);	

-- Private posts
-- Table
create table private_posts(user_id integer,private_post_id integer,private_post_time timestamptz,views integer,likes integer,deleted boolean,primary key(user_id,private_post_id));
--  Return next post id blah blahs
select max(private_post_id) from private_posts where user_id=%s;

-- Make a public post once client confirms.
insert into private_posts(user_id,private_post_id,private_post_time,views,likes,deleted) values(user_id_,new_post_id,current_timestamp,0,0,false);
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
	-- Do not commit inside a procedure while psycopg.. Use connection.commit()
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
			-- >> use the same public func as template


-- Search nearby people
select user_id from user_last_location where ST_DWithin(last_location, ST_MakePoint(2,3)::geography, 5000) and user_id=(select id from auth_user where username like '%search_query_here%')
-- ToDo
	-- Find nearby people
-- public_feed

