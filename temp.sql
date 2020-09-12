update public_posts set deleted=true where user_id=122 and public_post_id=2;

select public_feed_first_request(121);

insert into public_posts(user_id,public_post_id,public_post_location,public_post_time,views,likes,dislikes,deleted) values(122,5,ST_MakePoint(1,2),current_timestamp,0,0,0,false);

create or replace function public_feed_first_request(post_req_sender_id integer)
  returns table (user_id_ integer,public_post_id_ integer,views_ integer,likes_ integer,dislikes_ integer)
as
$$
declare
	last_location_ geography;
begin
	select last_location into last_location_ from user_last_location where user_id=post_req_sender_id;
	return query select user_id,public_post_id,views,likes,dislikes from public_posts WHERE ST_DWithin(public_post_location,last_location_, 5000) order by public_post_time desc limit 10;
end;
$$
language plpgsql;

select public_feed_first_request(121);

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
	return query SELECT user_id,public_post_id,views,likes,dislikes FROM public_posts WHERE ST_DWithin(public_post_location,last_location_, 5000) and public_post_time<(last_post_timestamp) order by public_post_time desc limit 10;
end;
$$
language plpgsql;
select public_feed_subsequent_request(121,122,2);