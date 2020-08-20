-- Fresh content
-- New posts available?
check if a row with certain condition exists?
i.e posts "newer" than first received post (by client)
-- Return new posts










-- Moved content
CREATE OR REPLACE PROCEDURE make_private_post(
	user_id_ integer
)
LANGUAGE 'plpgsql'
AS $BODY$
declare
	new_post_id integer; 
BEGIN
	select max(private_post_id) into new_post_id from private_posts where user_id=user_id_;
	raise notice ' Old private_post_id for user_id % is %',user_id_,new_post_id;
	new_post_id:=new_post_id+1;
	raise notice ' New private_post_id for user_id % is %',user_id_,new_post_id;
	insert into private_posts(user_id,private_post_id,private_post_time,views,likes) values(user_id_,new_post_id,current_timestamp,0,0);
	commit;
	raise notice 'Private post created successfully by %',user_id_;
END;
$BODY$;
call make_private_post(1);

-- LW
-- my_public_posts
select user_id,public_post_id,views,likes,dislikes from public_posts where user_id=1 order by public_post_time desc;
-- my_private_posts
select user_id,private_post_id,views,likes from private_posts where user_id=1 order by private_post_time desc;
-- delete public post
update public_posts set deleted=true where user_id=1 and public_post_id=1;


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

insert into followers (follower_id,followee_id) values (1,2);
insert into follow_requests (req_sender_id,req_receiver_id,req_time) values (3,4,current_timestamp);
select return_follow_status(5,6);
select return_follow_status(3,4);
select return_follow_status(1,2);


